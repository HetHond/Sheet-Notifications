import time
import gspread
from .sms_client import send_sms_message
from .utils.helpers import flatten, euro_float


def start_monitoring(gclient: gspread.Client, vonage_sms_client, spreadsheets):
    prev_condition_results = [[] for _ in range(0, len(spreadsheets))]
    while True:
        for spreadsheet_index in range(0, len(spreadsheets)):
            spreadsheet = spreadsheets[spreadsheet_index]
            spreadsheet_id = spreadsheet['spreadsheet_id']
            worksheet_id = spreadsheet['worksheet_id']
            monitors = spreadsheet['monitors']

            # Add ranges to batch get request
            batch_ranges = []
            for monitor in monitors:
                batch_ranges.append(monitor['range'])

            result = gclient.open_by_key(spreadsheet_id).get_worksheet_by_id(worksheet_id).batch_get(batch_ranges)
            prev_results = prev_condition_results[spreadsheet_index]
            if not len(prev_results):
                prev_results = [False for _ in range(0, len(monitors))]

            for monitor_index in range(0, len(monitors)):
                monitor = monitors[monitor_index]
                values = flatten(result[monitor_index])

                # Something has changed so check for the conditions now
                conditions = []
                for condition in monitor['conditions']:
                    condition_type = condition['type']
                    condition_value = condition['value']

                    try:
                        conditions.append(
                            (condition_type == '==' and
                             all(euro_float(value) == condition_value for value in values)) or
                            (condition_type == '!=' and
                             all(euro_float(value) != condition_value for value in values)) or
                            (condition_type == '<' and
                             all(euro_float(value) < condition_value for value in values)) or
                            (condition_type == '<=' and
                             all(euro_float(value) <= condition_value for value in values)) or
                            (condition_type == '>' and
                             all(euro_float(value) > condition_value for value in values)) or
                            (condition_type == '>=' and
                             all(euro_float(value) >= condition_value for value in values))
                        )
                    except ValueError:
                        print("Type error")
                        print(values)
                        conditions.append(False)
                        break

                # Check if anything has changed since the last time and if all conditions are met
                should_alert = all(conditions)
                if should_alert and (not len(prev_results) or not prev_results[monitor_index]):
                    # Send alerts
                    if 'sms' in monitor:
                        sms_config = monitor['sms']
                        text = sms_config['text'].format(value=values, range=monitor['range'])
                        send_sms_message(vonage_sms_client, sms_config['from'], sms_config['to'], text)

                prev_results[monitor_index] = should_alert

            prev_condition_results[spreadsheet_index] = prev_results

        time.sleep(30)
        