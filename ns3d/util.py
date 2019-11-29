import colorsys
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

def network_color_for(network, number_of_networks):
    hue = float(network) / float(number_of_networks + 1)
    rgb = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
    return (int(rgb[0]*255.0), int(rgb[1]*255.0), int(rgb[2]*255.0))
