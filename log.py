from datetime import datetime


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def color(text: str, color: bcolors) -> str:
    return str(color) + str(text) + str(bcolors.ENDC)


def log(text: str, level="NORMAL", write_to_file=True):
    logfile = "./log.txt"

    if write_to_file:
        with open(logfile, "a") as file:
            file.write(
                f"{str(datetime.now()).ljust(30)}{level.ljust(10)}{text}\n"
            )

    text = {
        "NORMAL": text,
        "ERROR": color(text, bcolors.FAIL),
        "WARNING": color(text, bcolors.WARNING),
        "INFO1": color(text, bcolors.OKBLUE),
        "INFO2": color(text, bcolors.OKCYAN),
        "SUCCESS": color(text, bcolors.OKGREEN)
    }[level]
    print(text)


def error(text: str, write_to_file=True):
    log(text, "ERROR", write_to_file)


def warn(text: str, write_to_file=True):
    log(text, "WARNING", write_to_file)


def info1(text: str, write_to_file=True):
    log(text, "INFO1", write_to_file)


def info2(text: str, write_to_file=True):
    log(text, "INFO2", write_to_file)


def success(text: str, write_to_file=True):
    log(text, "SUCCESS", write_to_file)
