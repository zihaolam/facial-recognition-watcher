import asyncio

# Decorator implementation of async runner !!


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


def get_largest_face(faces):
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
