import configparser
from Resources.Consts import SAVE_PATH


class ConfigManager:
    config = configparser.ConfigParser()
    config.read(SAVE_PATH)

    @staticmethod
    def SaveConfig():
        with open(SAVE_PATH, "w") as configfile:
            ConfigManager.config.write(configfile)
