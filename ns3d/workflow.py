import logging
import threading

logger = logging.getLogger(__name__)

class Workflow:
    def __init__(self):
        self.close = threading.Event()

    def stop(self):
        self.close.set()

    def start(self, workflow):
        thread = threading.Thread(target=workflow, args=(self,))
        thread.start()

    def __closed(self):
        raise Exception('Simulation stopped')

    def __check_close(self):
        if self.close.is_set():
            self.__closed()

    def sleep(self, duration):
        logger.debug('Sleep for %gs', duration)
        close = self.close.wait(duration)
        logger.debug('Close %s', close)
        if close is True:
            self.__closed()

    def until(self, condition):
        logger.error('Method workflow.until(%s) not yet implemented', condition)
