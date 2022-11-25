from typing import Tuple, Union
import requests
import constants
from requests.exceptions import HTTPError
from helpers import Spinner

# date_to_select: date = date.today().strftime("%Y-%m-%d")


def parse_user_pk(user_pk: str):
    return user_pk.split("::")[1].replace('_', ' ').title()


def get_events():
    try:
        response = requests.get(
            f"{constants.ENDPOINT_URL}/event")
        response.raise_for_status()
    except HTTPError as e:
        print(e)
        return None
    events = response.json()["body"]

    if isinstance(events, list):
        return events

    return None


def post_attendance(base64_img: str, event_id: str) -> Tuple[dict, bool]:
    try:
        response = requests.post(url=f"{constants.ENDPOINT_URL}/attendance", json={
            "face_image": f"data:image/jpeg;base64,{base64_img}", "event_id": event_id})
        response.raise_for_status()
        json_body = response.json()
        if "errorMessage" in json_body or json_body["statusCode"] >= 400:
            raise HTTPError()
        return json_body, True

    except HTTPError as e:
        return response.json(), False
