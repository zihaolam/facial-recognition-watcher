import app
import inquirer

from api import get_events

events = []


event_filter_selection = {
    "FILTER_BY_DATE": "Filter by date",
    "SHOW_ALL": "Show All"
}


def view_and_select_events():
    def event_label(event: dict):
        return f"{event.get('date')} - {event.get('name')}"
    events: list = get_events()

    if events is None:
        return None

    q_1 = [inquirer.List('filter', message="Filter by all or show date?", choices=list(
        event_filter_selection.values()), carousel=True)]
    ans_1 = inquirer.prompt(q_1)

    try:
        if ans_1.get('filter') == event_filter_selection["FILTER_BY_DATE"]:
            date_filter_input = input("Input Filter Date: ")
            events = [event for event in events if event["date"]
                      == date_filter_input]

        if not isinstance(events, list):
            print("There are no events")
            exit(0)

    except Exception as e:
        print("There are no events on this date")

    q_2 = [inquirer.List('event_id', message="Select Event of the day: ",
                         choices=[event_label(event) for event in events], carousel=True)]

    ans_2 = inquirer.prompt(q_2)
    selected_event = ans_2.get('event_id')
    event = next(
        (event for event in events if event_label(event) == selected_event), None)
    return event["pk"]


def start_recording_attendance(event_id):
    app.run(event_id)


if __name__ == "__main__":
    selected_event_id = view_and_select_events()
    if selected_event_id is None:
        print("No events")
        exit(0)
    start_recording_attendance(selected_event_id)
