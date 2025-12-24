import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")
    CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", 8123))
    CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER")
    CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")
    
    # External API (Mocking for now as credentials were not provided)
    EXTERNAL_API_URL = os.getenv("EXTERNAL_API_URL", "https://mock-api.com/dicom/v2/studies")
    EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY", "")

config = Config()
