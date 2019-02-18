from .ConditionalEvent import ConditionalEvent


def when(condition, globals, locals):
    return ConditionalEvent(condition, globals, locals)
