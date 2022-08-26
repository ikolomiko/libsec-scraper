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


def error(text: str):
    print(color(text, bcolors.FAIL))


def warn(text: str):
    print(color(text, bcolors.WARNING))


def info1(text: str):
    print(color(text, bcolors.OKBLUE))


def info2(text: str):
    print(color(text, bcolors.OKCYAN))


def success(text: str):
    print(color(text, bcolors.OKGREEN))
