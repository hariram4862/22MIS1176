from dotenv import load_dotenv
import os


load_dotenv(".env")


class Settings:
    BASE_URL = os.getenv("BASE_URL", "http://4.224.186.213/evaluation-service")
    AUTH_TOKEN = os.getenv("AUTH_TOKEN")
    DEFAULT_TOP_N = int(os.getenv("PRIORITY_TOP_N", "10"))


settings = Settings()

