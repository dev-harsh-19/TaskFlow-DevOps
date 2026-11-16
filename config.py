"""Application configuration."""

import os
import secrets


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    DATABASE = os.environ.get(
        "TASKFLOW_DATABASE",
        os.path.join(os.path.dirname(__file__), "instance", "tasks.sqlite3"),
    )
    TITLE_MAX_LENGTH = 120
    DESCRIPTION_MAX_LENGTH = 2000
    MAX_CONTENT_LENGTH = 1 * 1024 * 1024
