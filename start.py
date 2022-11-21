import app
import inquirer

from api import get_events

events = []


def view_and_select_events():
    def event_label(event):
        return f"{event.get('date')} - {event.get('name')}"
    events: list = get_events()

    questions = [inquirer.List('event_id', message="Select Event of the day: ",
                               choices=[event_label(event) for event in events], carousel=True)]

    answers = inquirer.prompt(questions)
    selected_event = answers.get('event_id')
    event = next(
        (event for event in events if event_label(event) == selected_event), None)
    return event["pk"]


def start_recording_attendance(event_id):
    app.run(event_id)


if __name__ == "__main__":
    selected_event_id = view_and_select_events()
    start_recording_attendance(selected_event_id)
