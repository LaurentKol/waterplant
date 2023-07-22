from datetime import datetime

class BaseSensor:
    def __init__(self, type: str, name: str) -> None:
        self.type = type
        self.name = name
        self.last_successful_reading_ts = datetime.now()
        self.last_successful_reading_and_no_notification_ts = datetime.now()
        self.consecutive_failed_reading = 0
