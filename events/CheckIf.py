from .CommandEvent import CommandEvent


def every(seconds):
    return CommandEvent(seconds, None)


def check_if(command):
    return CommandEvent(-1, command)

