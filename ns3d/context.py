import logging
import collections
import threading

logger = logging.getLogger(__name__)

class ThreadLocalStack:

    def __init__(self):
        self.data = threading.local()

    @property
    def stack(self):
        if not hasattr(self.data, 'stack'):
            self.data.stack = []
        return self.data.stack

    def push(self, item):
        self.stack.append(item)

    def pop(self):
        return self.stack.pop()

    def top(self):
        return self.stack[-1] if self.stack else None

class Context:
    __stack = ThreadLocalStack()

    @staticmethod
    def current():
        return Context.__stack.top()

    def __init__(self):
        self.fails = 0

    def defer(self, item):
        raise NotImplementedError

    def cancel(self, item):
        raise NotImplementedError

    def cleanup(self):
        raise NotImplementedError

    def add_error(self, err: Exception): # pylint: disable=unused-argument
        self.fails += 1

    def __enter__(self):
        Context.__stack.push(self)
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        assert Context.__stack.pop() is self, 'Invalid context stack, not the same number of push and pop operations'

class DeferredItem:

    def __init__(self, ctx: Context, name: str, func: callable, args, kwargs):
        self.ctx = ctx
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def cancel(self):
        self.ctx.cancel(self)

    def cleanup(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as err: # pylint: disable=broad-except
            logger.error('Failed to cleanup deferred item %s: %s', self.name, err)
            self.ctx.add_error(err)

    def __str__(self):
        return self.name

def defer(name, func, *args, **kwargs):
    if name is None:
        name = func.__qualname__

    ctx = Context.current()
    if ctx is None:
        logging.warning('No context available to defer %s', name)
        ctx = NoContext()

    item = DeferredItem(ctx, name, func, args, kwargs)
    ctx.defer(item)
    return item

class NoContext(Context):

    def defer(self, item):
        pass

    def cancel(self, item):
        pass

    def cleanup(self):
        pass

class SimpleContext(Context):

    def __init__(self):
        super().__init__()
        self.dequeue = collections.deque()

    def defer(self, item):
        logger.debug('Added deferred item: %s', item)
        self.dequeue.appendleft(item)

    def cancel(self, item):
        logger.debug('Removed deferred item: %s', item)
        self.dequeue.remove(item)

    def cleanup(self):
        logger.info('Cleanup %d items', len(self.dequeue))
        while self.dequeue:
            item = self.dequeue.popleft()
            logger.debug('Cleanup deferred item: %s', item)
            item.cleanup()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        super().__exit__(exc_type, exc_value, exc_traceback)
        self.cleanup()
