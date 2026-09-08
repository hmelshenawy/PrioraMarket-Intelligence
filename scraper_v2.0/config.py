# config.py
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Keys:
    ALGOLIA_APP_ID: str = os.getenv("ALGOLIA_APP_ID")
    ALGOLIA_API_KEY: str = os.getenv("ALGOLIA_API_KEY")
    ALGOLIA_INDEX: str = os.getenv("ALGOLIA_INDEX")
    ALGOLIA_URL: str = os.getenv("ALGOLIA_URL")
    ALGOLIA_URL2: str = os.getenv("ALGOLIA_URL2")


KEYS = Keys()