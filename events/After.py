from .TimedEvent import TimedEvent


def after(seconds):
    return TimedEvent(seconds)
