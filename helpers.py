import asyncio
import sys
import threading
import time
from typing import Tuple

# Decorator implementation of async runner !!


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\':
                yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False


def run_async(callback, loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    def inner(func):
        def wrapper(*args, **kwargs):
            def __exec():
                out = func(*args, **kwargs)
                callback(out)
                return out

            return loop.run_in_executor(None, __exec)

        return wrapper

    return inner


def get_largest_face(faces) -> Tuple[float, Tuple[float, float, float, float]]:
    size = 0
    coordinates = faces[0] if len(faces) else [0, 0, 0, 0]

    for face in faces:
        w = face.width()
        h = face.height()
        x = face.left()
        y = face.top()
        if w*h > size:
            size = w*h
            coordinates = (x, y, w, h)

    return size != 0, coordinates
