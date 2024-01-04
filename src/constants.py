# File containing all global constants

GOOGLE_SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "spreadsheets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "spreadsheet_id": {"type": "string"},
                    "worksheet_id": {"type": "string"},
                    "monitors": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "range": {"type": "string"},
                                "conditions": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "type": {"type": "string"},
                                            "value": {"type": "number"}
                                        },
                                        "required": ["type", "value"]
                                    }
                                },
                                "sms": {
                                    "type": "object",
                                    "properties": {
                                        "from": {"type": "string"},
                                        "to": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "text": {"type": "string"}
                                    },
                                    "required": ["from", "to", "text"]
                                }
                            },
                            "required": ["range", "conditions"],
                            "additionalProperties": False
                        }
                    }
                },
                "required": ["spreadsheet_id", "worksheet_id", "monitors"],
                "additionalProperties": False
            }
        }
    },
    "required": ["spreadsheets"],
    "additionalProperties": False
}
