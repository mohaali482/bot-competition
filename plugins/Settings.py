import os
import json

from dotenv import load_dotenv

load_dotenv()

FILE_DIR = "files/"
LOGS_DIR = "logs/logs.log"

API = os.getenv('API')

SuperUser = json.loads(os.getenv('SuperUser'))