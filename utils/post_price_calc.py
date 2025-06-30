import requests
import os
import sys
import json
import django
from pathlib import Path
from config import settings


project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


def calculate_price():
    return 500000 / 10
