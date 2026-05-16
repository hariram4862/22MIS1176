def optimize_tasks(tasks, max_hours):

    n = len(tasks)

    dp = [[0 for _ in range(max_hours + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):

        duration = tasks[i - 1]["Duration"]
        impact = tasks[i - 1]["Impact"]

        for hours in range(max_hours + 1):

            if duration <= hours:

                dp[i][hours] = max(
                    impact + dp[i - 1][hours - duration],
                    dp[i - 1][hours]
                )

            else:

                dp[i][hours] = dp[i - 1][hours]

    selected_tasks = []

    hours = max_hours

    for i in range(n, 0, -1):

        if dp[i][hours] != dp[i - 1][hours]:

            selected_tasks.append(tasks[i - 1])

            hours -= tasks[i - 1]["Duration"]

    selected_tasks.reverse()

    return {
        "total_impact": dp[n][max_hours],
        "total_duration": sum(task["Duration"] for task in selected_tasks),
        "selected_tasks": selected_tasks
    }