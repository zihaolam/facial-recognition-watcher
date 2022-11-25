import os
from dotenv import load_dotenv

load_dotenv()

is_prod = os.environ.get("STAGE") == "prod"

ENDPOINT_URL = "http://localhost:8081" if not is_prod else "https://wm7ph0zl23.execute-api.ap-southeast-1.amazonaws.com"

color_map = dict(success=(0, 255, 0), info=(255, 0, 0), danger=(0, 0, 255))
