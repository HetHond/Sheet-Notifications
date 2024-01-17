# Third-party imports
import vonage


def send_sms_message(vonage_sms_client: vonage.Sms, sender: str, receiver, text):
    if not isinstance(receiver, list):
        receiver = [receiver]

    for phone in receiver:
        response = vonage_sms_client.send_message({
            'from': sender,
            'to': phone,
            'text': text
        })
        if response['messages'][0]['status'] == '0':
            print(f'Successfully sent sms message to {receiver} -> {text}')
        else:
            error_text = response['messages'][0]['error-text']
            print(f'Failed to send sms message to {receiver} -> {error_text}')
