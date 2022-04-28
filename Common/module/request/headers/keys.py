import configparser
import os

current_path = os.path.dirname(os.path.realpath(__file__))
keys_path = os.path.join(current_path, "keys.ini")


conf = configparser.RawConfigParser()
conf.optionxform = lambda option: option
# conf = configparser.ConfigParser()
conf.read(keys_path, encoding="utf-8")  # python3
sections = conf.sections()


def read_default_header_keys():
    return [k for k, v in conf.items('default') if v == "1"]


def read_extend_header_keys():
    return [k for k, v in conf.items('extends') if v == "1"]


if __name__ == '__main__':
    print(read_default_header_keys())
    print(read_extend_header_keys())
