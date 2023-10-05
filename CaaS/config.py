from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.getcwd(), ".env"))

PORT = int(os.environ.get("PORT"))
if not PORT:
    print(Warning("Port is not found int the config Defaulting to the default port."))
    PORT = 8000

DB_URL = os.environ.get("DB_URL")
if not DB_URL:
    raise Exception("Database url not found in the config.")
    exit(1)
