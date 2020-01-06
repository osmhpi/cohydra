import logging
import threading

logger = logging.getLogger(__name__)

class Workflow:
    """! A workflow is a contains a list of commands for
    planned execution during the simulation.
    """
    def __init__(self):
        self.close = threading.Event()

    def stop(self):
        """! Stop the workflow."""
        self.close.set()

    def start(self, workflow):
        """! Start the workflow."""
        thread = threading.Thread(target=workflow, args=(self,))
        thread.start()

    def __closed(self):
        raise Exception('Simulation stopped')

    def __check_close(self):
        if self.close.is_set():
            self.__closed()

    def sleep(self, duration):
        """! Sleep and wait.

        @param duration The duration to sleep in seconds.
        """
        logger.debug('Sleep for %gs.', duration)
        close = self.close.wait(duration)
        logger.debug('Close %s.', close)
        if close is True:
            self.__closed()

    def until(self, condition):
        logger.error('Method workflow.until(%s) not yet implemented', condition)
