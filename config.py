import sys
import configparser


class ConfigReader:
    def __init__(self, filename="config.ini"):
        self.config = configparser.ConfigParser()
        self.filename = filename

        if not self.config.read(filename):
            print(f"Config file '{filename}' not found.", file=sys.stderr)

    def get_setting(self, section, key, default=None, as_type=str):
        try:
            value = self.config.get(section, key)
            return as_type(value)
        except (
            configparser.NoSectionError,
            configparser.NoOptionError,
            ValueError,
        ) as e:
            print(
                f"Error retrieving value for key '{key}' in section '{section}': {e}",
                file=sys.stderr,
            )
            return default
