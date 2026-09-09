import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "hotel-ai-sih-2026-secret"
    )

    DATABASE = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "hotel.db"
    )