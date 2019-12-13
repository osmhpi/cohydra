import argparse
import logging

class ArgumentParser(argparse.ArgumentParser):
    """! A simple-to-use argument parser for log levels.

    ArgumentParser by default defines the `--verbose` and `--log-level` flag.
    It is used to abstract these flags away and prevent repetition in the example scenarios.
    --verbose sets the overall log level to `DEBUG`.
    Valid options for log-level are `INFO` and `DEBUG`.
    """
    def __init__(self, *args, logger=None, **kvargs):
        super().__init__(*args, **kvargs)
        self.setup_logging = True
        self.logger_arg = 'logger' if logger is True else logger

    def run(self, main):
        """! Parse the arguments and pass them to a function to be called afterwards

        @param main The function to call and to pass the arguments to.
        """
        ns3d_name = __name__.rsplit('.', 1)[0]

        if self.setup_logging:
            default = 'INFO'
            self.add_argument('-v', '--verbose', action='store_const', const='DEBUG', default=default,
                              help=f'enable verbose logging for the {ns3d_name} logger', dest='log_level')
            self.add_argument('--log-level', default=default, help=f'log level for the {ns3d_name} logger')
            self.add_argument('--global-log-level', default=default, help='log level for the global logger')

        args = vars(self.parse_args())

        if self.setup_logging:
            log_level = args.pop('log_level')
            global_log_level = args.pop('global_log_level')

            logging.basicConfig(level=global_log_level)
            logging.getLogger().setLevel(global_log_level)
            logging.getLogger(ns3d_name).setLevel(log_level)

            logging.getLogger(__name__).debug('log_level=%s, global_log_level=%s', log_level, global_log_level)

            if self.logger_arg:
                args[self.logger_arg] = logging.getLogger(self.prog)
                args[self.logger_arg].setLevel(log_level)

        main(**args)
