from typing import Tuple
import numpy as np
import cv2
import time
from requests.exceptions import HTTPError
import constants
import base64
import helpers
import dlib
import traceback

from api import parse_user_pk, post_attendance


class App:
    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            'face_detection_model.xml')

        self.detector = dlib.get_frontal_face_detector()
        self.tracker = dlib.correlation_tracker()

        self.cam = cv2.VideoCapture(0)

        self.OUTPUT_SIZE_WIDTH = 775
        self.OUTPUT_SIZE_HEIGHT = 600

        if not self.cam.isOpened():
            print("Could not open cam")
            exit()

        self.face_present = False
        self.tracking_confirmation_counter = 0

    def start_tracking(self, frame, ret):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray)

        # Counter to count number of faces
        i = 0

        present, (x, y, w, h) = helpers.get_largest_face(faces)

        if present and ret:
            top = y
            left = x
            right = x + w
            bottom = y+h

            face_image = frame[top:bottom, left:right].copy()
            try:
                _, buffer = cv2.imencode('.jpg', face_image)
                base64_img = base64.b64encode(buffer).decode("utf-8")

                self.tracker.start_track(
                    frame, dlib.rectangle(left, top, right, bottom)
                )

                return base64_img, (x, y, w, h)

            except Exception as e:
                traceback.print_exc()
                print(e)

        return None, (None, None, None, None)

    def track_face(self, frame) -> Tuple[float, Tuple[int, int, int, int]]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        quality = self.tracker.update(gray) > 7
        pos = self.tracker.get_position()
        left = int(pos.left())
        top = int(pos.top())
        right = int(pos.right())
        bottom = int(pos.bottom())
        return quality, (left, top, right-left, bottom-top)


def retry_request(callback, retry_limit):
    retry_count = 0
    response = callback()
    while response is None and retry_count < retry_limit:
        response = callback()

    return response


def draw_rectangle(frame, x, y, w, h, border_type="info"):
    return cv2.rectangle(frame, (x, y-50), (x + w, y + h), constants.color_map.get(border_type, constants.color_map["info"]), 2)


def draw_caption(frame, x, y, text, message_type="info"):
    if x is None or y is None:
        return
    return cv2.putText(frame, text, (x, y-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, constants.color_map.get(message_type, constants.color_map["info"]), 2)


def run(event_id: str):
    caption = None
    app = App()
    controls_color = "info"

    while True:
        # Capture frame-by-frame
        ret, frame = app.cam.read()
        frame = cv2.flip(frame, 1)

        if not app.face_present:
            base64_img, (x, y, w, h) = app.start_tracking(
                frame, ret=ret)

            if base64_img is not None:
                app.tracking_confirmation_counter += 1
            if base64_img is not None and app.tracking_confirmation_counter >= 10:
                app.face_present = True
                response, ok = post_attendance(base64_img, event_id)

                if ok:
                    controls_color = "success"
                    caption = parse_user_pk(response["body"]["pk"])

                else:
                    caption = "Unregistered User"
                    controls_color = "danger"
                    app.tracking_confirmation_counter = 0
                    app.face_present = False

        else:
            app.face_present, (x, y, w, h) = app.track_face(
                frame)
            if not app.face_present:
                caption = None
                app.tracking_confirmation_counter = 0
                controls_color = "info"

        if x is not None and y is not None and w is not None and h is not None:
            draw_rectangle(frame, x, y, w, h, border_type=controls_color)

        if caption is not None:
            draw_caption(frame, x, y, caption, message_type=controls_color)

        cv2.imshow('frame', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    app.cam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run()
