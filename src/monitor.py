# Standard library imports
import time
from datetime import datetime

# Third-party imports
import gspread

# Local application/library specific imports
from .sms_client import send_sms_message
from .utils.helpers import flatten, euro_float


def start_monitoring(gclient: gspread.Client, vonage_sms_client, spreadsheets, interval):
    prev_condition_results, debounce_record = initialize_monitoring(spreadsheets)

    # Monitoring loop
    while True:
        for spreadsheet_index, spreadsheet in enumerate(spreadsheets):
            process_spreadsheet(gclient, vonage_sms_client, spreadsheet, spreadsheet_index, prev_condition_results,
                                debounce_record)

        print(f'Waiting for {interval} seconds')
        time.sleep(interval)


def initialize_monitoring(spreadsheets):
    """ Initialize monitoring data structures. """
    prev_condition_results = [[]] * len(spreadsheets)
    debounce_record = [[0] * len(sheet['monitors']) for sheet in spreadsheets]
    return prev_condition_results, debounce_record


def process_spreadsheet(gclient, vonage_sms_client, spreadsheet, spreadsheet_index, prev_condition_results,
                        debounce_record):
    """ Process each spreadsheet for monitoring. """
    batch_ranges = [monitor['range'] for monitor in spreadsheet['monitors']]
    result = fetch_spreadsheet_data(gclient, spreadsheet['spreadsheet_id'], spreadsheet['worksheet_id'], batch_ranges)

    prev_results = prev_condition_results[spreadsheet_index]
    if not prev_results:
        prev_results = [True] * len(spreadsheet['monitors'])

    for monitor_index, monitor in enumerate(spreadsheet['monitors']):
        values = flatten(result[monitor_index])
        conditions_met = evaluate_conditions(monitor, values)

        if conditions_met and not prev_results[monitor_index]:
            handle_alert(vonage_sms_client, monitor, values, spreadsheet_index, monitor_index, debounce_record)

        prev_results[monitor_index] = conditions_met

    prev_condition_results[spreadsheet_index] = prev_results


def fetch_spreadsheet_data(gclient, spreadsheet_id, worksheet_id, batch_ranges):
    """ Fetch data from a Google spreadsheet. """
    try:
        worksheet = gclient.open_by_key(spreadsheet_id).get_worksheet_by_id(worksheet_id)
        return worksheet.batch_get(batch_ranges)
    except gspread.exceptions.APIError as e:
        print(f"API error occurred: {e}")
        return [[] for _ in range(len(batch_ranges))]


def evaluate_conditions(monitor, values):
    """ Evaluate conditions for a given monitor. """
    conditions = []
    for condition in monitor['conditions']:
        try:
            conditions.append(check_condition(condition, values))
        except ValueError:
            print("Type error with values:", values)
            return False
    return all(conditions)


def check_condition(condition, values):
    """ Check a single condition against given values. """
    condition_type = condition['type']
    condition_value = condition['value']
    return all(
        (condition_type == '==' and euro_float(value) == condition_value) or
        (condition_type == '!=' and euro_float(value) != condition_value) or
        (condition_type == '<' and euro_float(value) < condition_value) or
        (condition_type == '<=' and euro_float(value) <= condition_value) or
        (condition_type == '>' and euro_float(value) > condition_value) or
        (condition_type == '>=' and euro_float(value) >= condition_value)
        for value in values
    )


def handle_alert(vonage_sms_client, monitor, values, spreadsheet_index, monitor_index, debounce_record):
    """ Handle alerting logic for SMS. """
    current_timestamp = datetime.now().timestamp()
    if 'debounce' in monitor:
        debounce_time = monitor['debounce']
        if current_timestamp - debounce_record[spreadsheet_index][monitor_index] > debounce_time:
            send_alert(vonage_sms_client, monitor, values)
        debounce_record[spreadsheet_index][monitor_index] = current_timestamp
    else:
        send_alert(vonage_sms_client, monitor, values)


def send_alert(vonage_sms_client, monitor, values):
    """ Send an SMS alert. """
    if 'sms' in monitor:
        sms_config = monitor['sms']
        text = sms_config['text'].format(value=values, range=monitor['range'])
        send_sms_message(vonage_sms_client, sms_config['from'], sms_config['to'], text)