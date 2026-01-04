# app/core/config.py

class Settings:
    # ===============================
    # PIPELINE LIMITS
    # ===============================
    MAX_NODES: int = 10_000
    MAX_EDGES: int = 50_000
    MAX_NODE_ID_LENGTH: int = 256
    MAX_EDGE_ID_LENGTH: int = 256

    # ===============================
    # CACHE
    # ===============================
    ENABLE_CACHING: bool = True
    CACHE_TTL: int = 300  # seconds

    # ===============================
    # RATE LIMITING
    # ===============================
    RATE_LIMIT_ANONYMOUS: str = "100/minute"
    RATE_LIMIT_PARSE: str = "50/minute"

    # ===============================
    # CORS
    # ===============================
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    # ===============================
    # APP METADATA
    # ===============================
    APP_NAME: str = "Pipeline Analysis API"
    VERSION: str = "2.0.0"


settings = Settings()
