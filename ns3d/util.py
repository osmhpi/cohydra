import functools
import weakref

# from http://stackoverflow.com/questions/4103773/efficient-way-of-having-a-function-only-execute-once-in-a-loop
def once(func):
    """Runs a method (successfully) only once per instance.
    """

    has_run = weakref.WeakSet()

    name = func.__name__
    name = f'__has_run_{name}_once'

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        first = args[0] if len(args) > 0 else once
        if first not in has_run:
            result = func(*args, **kwargs)
            has_run.add(first)
            return result

    return wrapper
