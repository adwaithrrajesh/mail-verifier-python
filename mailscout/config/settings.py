import os
from dotenv import load_dotenv

def load_config():
    load_dotenv()

    global SETTINGS
    SETTINGS = {
        "SMTP_TIMEOUT": int(os.getenv("SMTP_TIMEOUT", "8")),
        "NUM_THREADS": int(os.getenv("NUM_THREADS", "50")),
        "NUM_BULK_THREADS": int(os.getenv("NUM_BULK_THREADS", "25")),
        "BATCH_SIZE": int(os.getenv("BATCH_SIZE", "100")),
        "CONNECTION_POOL_SIZE": int(os.getenv("CONNECTION_POOL_SIZE", "50")),
        "MAX_RETRIES": int(os.getenv("MAX_RETRIES", "3")),
        "RETRY_DELAY": float(os.getenv("RETRY_DELAY", "1.0")),
        "RATE_LIMIT": int(os.getenv("RATE_LIMIT_PER_MINUTE", "500"))
    }
