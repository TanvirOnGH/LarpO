import os, platform
import sys
import multiprocessing
import sqlite3
import pytz
from datetime import datetime

from config import ConfigReader

config_reader = ConfigReader(filename="config.ini")

TIMEZONE = config_reader.get_setting("Misc", "time_zone")


class ChatLogger:
    def __init__(self, config_filename="config.ini"):
        self.config_reader = ConfigReader(filename=config_filename)
        self.database_file = self.config_reader.get_setting(
            "Database", "filename", default="chat_logs.db"
        )

    def _create_table(self):
        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author TEXT,
                content TEXT,
                response TEXT
            )
            """
        )

        connection.commit()
        connection.close()

    def log_to_database(self, author, content, response):
        self._create_table()

        connection = sqlite3.connect(self.database_file)
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO chat_logs (author, content, response)
            VALUES (?, ?, ?)
            """,
            (author, content, response),
        )

        connection.commit()
        connection.close()


def time_now(timezone=TIMEZONE):
    return (
        datetime.utcnow()
        .replace(tzinfo=pytz.utc)
        .astimezone(pytz.timezone(timezone))
        .strftime("%I:%M:%S %p %Y-%m-%d")
    )


def get_cores(logical=True):
    try:
        system_name = platform.system()
        if system_name == "Windows":
            result = os.popen("WMIC CPU Get DeviceID").read()
            cpu_count = len(set(result.strip().split("\n")[1:]))
        elif system_name == "Linux":
            cpu_count = multiprocessing.cpu_count()
        elif system_name in ["Darwin", "FreeBSD", "OpenBSD", "NetBSD"]:
            result = os.popen("sysctl -n hw.ncpu").read()
            cpu_count = int(result.strip())
        else:
            print("Unsupported operating system.", file=sys.stderr)
            return None

        return cpu_count if logical else cpu_count // 2

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None
