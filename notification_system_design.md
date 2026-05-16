# Notification System Design

This document presents a production-oriented backend design for a campus notification platform supporting inbox retrieval, real-time delivery, reliable fan-out, and priority ranking.

## Stage 1

### Core Features

- Fetch notifications
- Fetch unread notifications
- Mark notification as read
- Mark all notifications as read
- Delete notification
- Real-time notification delivery

### Notification Resource Schema

```json
{
  "id": "uuid",
  "type": "Placement",
  "title": "Placement Update",
  "message": "Amazon interview shortlist released",
  "isRead": false,
  "priority": "high",
  "createdAt": "timestamp"
}
```

### Common API Conventions

| Item | Standard |
|---|---|
| Base path | `/api/v1/notifications` |
| Auth | `Authorization: Bearer <token>` |
| Content type | `application/json` |
| Response envelope | `success`, `message`, `data` |
| Pagination | `page`, `limit`, and pagination metadata |
| Time format | ISO 8601 UTC timestamp |

### REST APIs

#### 1. Fetch Notifications

| Field | Value |
|---|---|
| Method | `GET` |
| Endpoint | `/api/v1/notifications` |
| Purpose | Retrieve notifications for the authenticated student in reverse chronological order |
| Headers | `Authorization: Bearer <token>` |
| Query Params | `page`, `limit`, `type`, `isRead`, `priority` |
| Request Body | None |

Sample response:

```json
{
  "success": true,
  "message": "Notifications fetched successfully",
  "data": {
    "items": [
      {
        "id": "9e616618-6040-4524-9c08-f9d9e4d1e6df",
        "type": "Placement",
        "title": "Placement Update",
        "message": "Amazon interview shortlist released",
        "isRead": false,
        "priority": "high",
        "createdAt": "2026-05-16T12:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 145,
      "hasNext": true
    }
  }
}
```

Status codes:

- `200 OK` - notifications returned
- `400 Bad Request` - invalid query params
- `401 Unauthorized` - missing or invalid token
- `500 Internal Server Error` - server-side failure

#### 2. Fetch Unread Notifications

| Field | Value |
|---|---|
| Method | `GET` |
| Endpoint | `/api/v1/notifications/unread` |
| Purpose | Return only unread notifications for the authenticated student |
| Headers | `Authorization: Bearer <token>` |
| Query Params | `page`, `limit`, `type`, `priority` |
| Request Body | None |

Sample response:

```json
{
  "success": true,
  "message": "Unread notifications fetched successfully",
  "data": {
    "items": [
      {
        "id": "9e616618-6040-4524-9c08-f9d9e4d1e6df",
        "type": "Placement",
        "title": "Placement Update",
        "message": "Amazon interview shortlist released",
        "isRead": false,
        "priority": "high",
        "createdAt": "2026-05-16T12:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 12,
      "hasNext": false
    }
  }
}
```

Status codes:

- `200 OK`
- `401 Unauthorized`
- `500 Internal Server Error`

#### 3. Mark Notification as Read

| Field | Value |
|---|---|
| Method | `PATCH` |
| Endpoint | `/api/v1/notifications/{id}/read` |
| Purpose | Mark a specific notification as read |
| Headers | `Authorization: Bearer <token>` |
| Query Params | None |
| Request Body | None |

Sample response:

```json
{
  "success": true,
  "message": "Notification marked as read",
  "data": {
    "id": "9e616618-6040-4524-9c08-f9d9e4d1e6df",
    "isRead": true,
    "readAt": "2026-05-16T12:35:00Z"
  }
}
```

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`
- `409 Conflict` - already marked read

#### 4. Mark All Notifications as Read

| Field | Value |
|---|---|
| Method | `PATCH` |
| Endpoint | `/api/v1/notifications/read-all` |
| Purpose | Mark all unread notifications as read for the authenticated student |
| Headers | `Authorization: Bearer <token>` |
| Query Params | None |
| Request Body | None |

Sample response:

```json
{
  "success": true,
  "message": "All notifications marked as read",
  "data": {
    "updatedCount": 12,
    "readAt": "2026-05-16T12:36:00Z"
  }
}
```

Status codes:

- `200 OK`
- `401 Unauthorized`
- `500 Internal Server Error`

#### 5. Delete Notification

| Field | Value |
|---|---|
| Method | `DELETE` |
| Endpoint | `/api/v1/notifications/{id}` |
| Purpose | Soft-delete or remove a notification from the user inbox |
| Headers | `Authorization: Bearer <token>` |
| Query Params | None |
| Request Body | None |

Sample response:

```json
{
  "success": true,
  "message": "Notification deleted successfully",
  "data": {
    "id": "9e616618-6040-4524-9c08-f9d9e4d1e6df",
    "deleted": true
  }
}
```

Status codes:

- `200 OK`
- `401 Unauthorized`
- `404 Not Found`

#### 6. Real-Time Notification Delivery

| Field | Value |
|---|---|
| Method | `GET` |
| Endpoint | `/api/v1/notifications/ws` |
| Purpose | Upgrade HTTP connection to WebSocket for live delivery |
| Headers | `Authorization: Bearer <token>` |
| Query Params | Optional auth fallback if handshake does not support headers |
| Request Body | None |

WebSocket event payload:

```json
{
  "event": "notification.created",
  "data": {
    "id": "9e616618-6040-4524-9c08-f9d9e4d1e6df",
    "type": "Placement",
    "title": "Placement Update",
    "message": "Amazon interview shortlist released",
    "isRead": false,
    "priority": "high",
    "createdAt": "2026-05-16T12:30:00Z"
  }
}
```

### Why WebSockets

- WebSockets maintain a persistent connection between client and server.
- They eliminate repeated polling overhead and reduce unnecessary database reads.
- They offer low-latency delivery, which is critical for placement, result, and event alerts.
- They fit live notification systems where updates are pushed immediately after creation.

### Simple Real-Time Architecture Flow

```text
Notification Producer -> Notification Service -> PostgreSQL
                                          -> WebSocket Gateway -> Connected Clients
```

### Stage 1 Conclusion

The API design follows standard REST conventions for inbox operations and uses WebSockets for low-latency delivery. This combination gives a predictable developer experience while supporting real-time campus communication at scale.

## Stage 2

### Database Choice: PostgreSQL

PostgreSQL is the preferred primary datastore because it provides:

- ACID compliance for reliable notification state transitions such as read, unread, and delete operations.
- Strong indexing support for inbox queries filtered by user, read status, and recency.
- Relational consistency for mapping users to notifications without data duplication.
- Mature support for partitioning, replication, and operational tooling as scale increases.

### SQL vs NoSQL Comparison

| Factor | SQL (PostgreSQL) | NoSQL |
|---|---|---|
| Consistency | Strong | Usually eventual by default |
| Relationships | Native joins and constraints | Often handled in application logic |
| Query flexibility | Rich filtering and ordering | Good for denormalized access patterns |
| Best fit here | User inbox state and transactional correctness | High-scale feed fan-out or event storage |

Final choice: PostgreSQL is the best fit because unread state, deletion state, filtering, and auditability are transactional and relational concerns.

### Logical Data Model

#### `users`

| Column | Type | Notes |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `student_id` | `bigint` | Unique campus student identifier |
| `name` | `varchar(120)` | Student name |
| `email` | `varchar(255)` | Unique email |
| `created_at` | `timestamptz` | Creation timestamp |

#### `notifications`

| Column | Type | Notes |
|---|---|---|
| `id` | `uuid` | Primary key |
| `notification_type` | `notification_type_enum` | `Event`, `Result`, `Placement` |
| `title` | `varchar(160)` | Notification title |
| `message` | `text` | Content |
| `priority` | `varchar(20)` | low, medium, high |
| `created_at` | `timestamptz` | Creation timestamp |
| `expires_at` | `timestamptz` | Optional TTL boundary |

#### `user_notifications`

| Column | Type | Notes |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `user_id` | `bigint` | FK to `users.id` |
| `notification_id` | `uuid` | FK to `notifications.id` |
| `is_read` | `boolean` | Default `false` |
| `read_at` | `timestamptz` | Nullable |
| `is_deleted` | `boolean` | Soft-delete flag |
| `created_at` | `timestamptz` | Delivery timestamp |

### Relationship Design

- `users` to `user_notifications` is one-to-many.
- `notifications` to `user_notifications` is one-to-many.
- A user can receive many notifications over time.
- A single notification template can be linked to many users using the junction table.

### Recommended Indexes

| Table | Index |
|---|---|
| `user_notifications` | `(user_id, is_read, created_at DESC)` |
| `user_notifications` | `(user_id, created_at DESC)` |
| `notifications` | `(notification_type, created_at DESC)` |
| `user_notifications` | `(created_at)` for partition pruning support |

Required focus areas:

- `user_id` accelerates per-student inbox retrieval.
- `is_read` supports unread-only filtering.
- `created_at` supports sorting by latest first.
- `notification_type` supports type-specific reporting.

### Scaling Concerns

- Large notification volume increases table size and index size.
- Read-heavy traffic creates repeated inbox fetches during page loads.
- Storage grows rapidly because each notification may fan out to many students.

### Scaling Solutions

- Partitioning: Partition `user_notifications` by time, such as monthly partitions, to reduce scan size.
- Archiving old notifications: Move cold data older than a retention threshold into archive tables or object storage.
- Redis caching: Cache the latest unread inbox snapshot or unread count for hot users.
- Read replicas: Offload read-heavy API traffic from the primary writer database.

### Stage 2 Conclusion

PostgreSQL is the right default choice because the system needs strong consistency, structured relationships, and efficient filtering. With partitioning, replicas, and caching, it can serve both transactional correctness and growing traffic.

## Stage 3

### Problem Query

The original query pattern is:

```sql
SELECT *
FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```

### Why This Query Becomes Slow

- If `studentID`, `isRead`, and `createdAt` are not indexed together, the optimizer may perform a full table scan.
- Sorting a large result set on `createdAt DESC` adds extra CPU and memory overhead.
- `SELECT *` increases I/O by reading unnecessary columns.
- At millions of rows, scanning and sorting on every request becomes expensive.

### Optimized Query

```sql
SELECT id, notification_type, title, message, is_read, created_at
FROM user_notifications
WHERE user_id = 1042
  AND is_read = false
  AND is_deleted = false
ORDER BY created_at DESC
LIMIT 20;
```

### Recommended Composite Index

```sql
CREATE INDEX idx_user_notifications_user_read_created
ON user_notifications (user_id, is_read, created_at DESC);
```

### Why Composite Index Is Better

- The query filters first by `user_id`, then by `is_read`, and finally sorts by `created_at DESC`.
- A composite index aligned to the exact access pattern allows the database to locate matching rows quickly and return them in the required order.
- This avoids separate filtering and sorting steps for most requests.

### Why Indexing Every Column Is Bad

- Memory overhead increases because each index consumes RAM and disk.
- Write performance degrades since inserts and updates must maintain every index.
- Index maintenance cost grows during vacuum, reindexing, and storage operations.
- Too many low-value indexes can confuse the optimizer rather than help it.

### Optimized Query for Placement Notifications in the Last 7 Days

```sql
SELECT DISTINCT un.user_id
FROM user_notifications un
JOIN notifications n
  ON n.id = un.notification_id
WHERE n.notification_type = 'Placement'
  AND n.created_at >= NOW() - INTERVAL '7 days'
  AND un.is_deleted = false;
```

Recommended supporting index:

```sql
CREATE INDEX idx_notifications_type_created
ON notifications (notification_type, created_at DESC);
```

### Stage 3 Conclusion

The slowdown is primarily caused by poor index alignment and unnecessary scanning plus sorting. A carefully designed composite index reduces lookup cost significantly while avoiding the operational penalty of indexing every column.

## Stage 4

### Problem Statement

Fetching notifications on every page load causes repetitive reads, elevated latency, and unnecessary database pressure. The solution should reduce direct database hits while preserving freshness for the student inbox.

### Scalable Solutions

#### 1. Redis Caching

- Improvement: Cache unread counts, latest notification pages, and user inbox summaries.
- Tradeoff: Cached data can become stale if invalidation is delayed.
- Additional concern: Memory usage must be controlled with TTLs and eviction policies.

#### 2. WebSockets

- Improvement: Push new notifications to clients instantly instead of forcing repeated polling.
- Tradeoff: Stateful connection management adds operational complexity.
- Additional concern: WebSocket scaling requires connection-aware load balancing or a pub/sub backplane.

#### 3. Lazy Loading

- Improvement: Load notifications only when the inbox panel is opened rather than on every page render.
- Tradeoff: First inbox open may show slightly higher latency.

#### 4. Pagination

- Improvement: Limit per-request rows and payload size, reducing CPU, I/O, and network cost.
- Tradeoff: Clients need additional requests for deep history.

#### 5. Background Sync

- Improvement: Mobile or web clients can periodically refresh counts and only fetch deltas in the background.
- Tradeoff: Sync interval tuning is required to balance freshness and cost.

#### 6. CDN for Static Assets

- Improvement: Offload frontend assets such as JS bundles, icons, and avatars so the application tier focuses on notification traffic.
- Tradeoff: Does not directly reduce notification query cost, but improves overall page performance.

### Recommended Architecture

```text
Client -> API Gateway -> Notification Service -> Redis -> PostgreSQL
```

### Flow

1. Client requests unread count or notification page.
2. API Gateway handles auth, rate limiting, and routing.
3. Notification Service checks Redis for cached inbox data.
4. On cache miss, Notification Service reads from PostgreSQL, returns the response, and populates Redis.
5. New notification events also flow through WebSockets to connected clients for immediate updates.

### Stage 4 Conclusion

The best approach is layered optimization rather than a single fix. Redis reduces hot-read pressure, WebSockets reduce polling, and pagination plus lazy loading control payload size, producing a scalable read path.

## Stage 5

### Problems in the Given Pseudocode

- Sequential processing makes throughput poor for large fan-out campaigns.
- Partial failures can leave state inconsistent if email succeeds but DB save fails, or vice versa.
- There is no retry strategy for transient failures.
- The workflow is blocking and cannot scale to tens of thousands of users reliably.
- A single slow downstream provider can stall the whole batch.

### Reliable Distributed Architecture

```text
API -> Queue -> Workers -> Email Service / Push Service
```

Recommended components:

- Kafka or RabbitMQ for durable asynchronous delivery.
- Worker consumers for email and push processing.
- Retry queues for transient failures such as SMTP timeout.
- Dead letter queue for poison messages or retry exhaustion.
- Idempotency keys to prevent duplicate notification delivery.

### Why DB Save Should Happen Before Email

- The database should be the source of truth for whether a notification exists for a user.
- Persisting first guarantees the system can recover, retry, audit, and display in-app state even if email delivery fails.
- This avoids sending a user an email for a notification that the platform cannot later show in the inbox.

### Why Async Processing Is Better

- The API becomes fast because it only validates input and enqueues work.
- Downstream operations execute independently and in parallel.
- Retries can happen without blocking user-facing requests.
- The system becomes eventually consistent, which is acceptable for campus notifications.

### Retry Handling if Email Fails Midway

- Worker marks the attempt as failed and republishes the message to a retry queue with backoff.
- If retry count exceeds threshold, the message moves to the dead letter queue.
- The in-app notification remains available because the DB write already succeeded.
- Operations teams can inspect the DLQ and replay failed jobs safely using idempotency keys.

### Improved Pseudocode

```text
function notify_all(student_ids, message):
    campaign_id = create_campaign_record(message)

    for student_id in student_ids:
        notification_id = save_notification_to_db(
            campaign_id=campaign_id,
            student_id=student_id,
            message=message,
            status="queued"
        )

        enqueue_job({
            "notification_id": notification_id,
            "student_id": student_id,
            "message": message,
            "idempotency_key": notification_id
        })

worker process_notification(job):
    push_to_app(job.student_id, job.message)

    try:
        send_email(job.student_id, job.message, job.idempotency_key)
        mark_notification_status(job.notification_id, "delivered")
    except TemporaryEmailError:
        retry_with_backoff(job)
    except PermanentEmailError:
        mark_notification_status(job.notification_id, "failed")
        move_to_dead_letter_queue(job)
```

### Stage 5 Conclusion

Asynchronous queue-based fan-out is the correct design for high-volume notification delivery. It improves throughput, isolates failures, supports retries, and preserves consistency by writing durable state before external side effects.

## Stage 6

### Requirement

Introduce a Priority Inbox that always returns the top `n` most important notifications first, without implementing code in this document.

### Ranking Strategy

Each notification receives a score derived from:

- Priority weight by type: `Placement > Result > Event`
- Read state: unread notifications receive a positive boost
- Recency: newer notifications receive a higher score

### Sample Scoring Formula

```text
priority_score =
  type_weight
  + unread_bonus
  + recency_factor
```

Example weights:

- `Placement = 100`
- `Result = 70`
- `Event = 40`
- `unread_bonus = 30 if isRead = false else 0`
- `recency_factor = max(0, 50 - age_in_hours)`

### Efficient Top-10 Retrieval

For a stream or large list of notifications, maintain a min heap of size `K = 10`.

Algorithm outline:

1. Compute the score for each notification.
2. Push the first `K` notifications into a min heap.
3. For each subsequent notification, compare its score with the heap root.
4. If the new score is higher, replace the root.
5. Return the heap contents sorted in descending order.

### Why Use a Heap

- A min heap keeps only the best `K` items in memory.
- Time complexity is `O(N log K)`, which is efficient when `K` is small and `N` is large.
- It is more scalable than sorting the entire dataset, which would cost `O(N log N)`.

### Priority Queue Justification

- Suitable when notifications continuously arrive and top results need to be recomputed efficiently.
- Supports incremental updates better than full-list resorting.
- Keeps compute cost predictable for top-10 style inboxes.

### Stage 6 Conclusion

The Priority Inbox should use score-based ranking with a bounded min heap for efficient top-`n` retrieval. This approach balances business relevance, unread emphasis, and recency while remaining computationally efficient.
