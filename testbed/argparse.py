"""Argument parsing for the simulation."""

import argparse
import logging
import os
import sys

class ArgumentParser(argparse.ArgumentParser):
    """A simple-to-use argument parser for log levels.

    ArgumentParser by default defines the `--verbose` and `--log-level` flag.
    It is used to abstract these flags away and prevent repetition in the example scenarios.
    `--verbose` sets the overall log level to `DEBUG`.
    Valid options for log-level are `INFO` and `DEBUG`.

    Parameters
    ----------
    logger : str
        The name of the logger argument to pass to the main function.
    """

    def run(self, main, setup_logging=True, logger_arg=None, needs_root=True):
        """Parse the arguments and pass them to a function to be called afterwards

        Parameters
        ----------
        main : callable
            The function to call and to pass the arguments to.
        setup_logging : bool
            Whether to set up logging with the default python logger and parse log levels.
        logger_arg : string
            The name of the argument to pass the logger to the :code:`main` function.
        needs_root : bool
            Whether the program needs root privileges. The argument parser will re-execute the program with sudo
            if code:`needs_root` is set and the current user is not root.
        """
        testbed_name = __name__.rsplit('.', 1)[0]

        if setup_logging:
            default = 'INFO'
            self.add_argument('-v', '--verbose', action='store_const', const='DEBUG', default=default,
                              help=f'enable verbose logging for the {testbed_name} logger', dest='log_level')
            self.add_argument('--log-level', default=default, help=f'log level for the {testbed_name} logger')
            self.add_argument('--global-log-level', default=default, help='log level for the global logger')

        args = vars(self.parse_args())

        if setup_logging:
            log_level = args.pop('log_level')
            global_log_level = args.pop('global_log_level')

            logging.basicConfig(level=global_log_level)
            logging.getLogger().setLevel(global_log_level)
            logging.getLogger(testbed_name).setLevel(log_level)

            logging.getLogger(__name__).debug('log_level=%s, global_log_level=%s', log_level, global_log_level)

            if logger_arg:
                args[logger_arg] = logging.getLogger(self.prog)
                args[logger_arg].setLevel(log_level)

        logging.getLogger(self.prog).info('uid=%s', os.getuid())

        if needs_root and os.getuid() != 0:
            logging.getLogger(self.prog).info('Reexecute with sudo')
            argv = ['sudo', '-E', 'env']
            for k, v in os.environ.items():
                if k.startswith('LD_') or k.endswith('_RLD') or k in self.__env_keep_manual:
                    argv.append(f'{k}={v}')
            argv.extend(sys.argv)
            os.execvp(argv[0], argv)
            # exec should never return
            exit(1)

        main(**args)

    # All 'Environment variables to remove' from `sudo sudo -V`.
    # All prefix or suffix matches are removed and hardcoded.
    # And `PATH` is missing in the list from `sudo sudo -V`.
    __env_keep_manual = [
        'BASH_ENV',
        'BASHOPTS',
        'CDPATH',
        'ENV',
        'FPATH',
        'GLOBIGNORE',
        'HOSTALIASES',
        'IFS',
        'JAVA_TOOL_OPTIONS',
        'LOCALDOMAIN',
        'NLSPATH',
        'NULLCMD',
        'PATH_LOCALE',
        'PATH',
        'PERL5DB',
        'PERL5LIB',
        'PERL5OPT',
        'PERLIO_DEBUG',
        'PERLLIB',
        'PS4',
        'PYTHONHOME',
        'PYTHONINSPECT',
        'PYTHONPATH',
        'PYTHONUSERBASE',
        'READNULLCMD',
        'RES_OPTIONS',
        'RUBYLIB',
        'RUBYOPT',
        'SHELLOPTS',
        'TERMCAP',
        'TERMINFO_DIRS',
        'TERMINFO',
        'TERMPATH',
        'TMPPREFIX',
        'ZDOTDIR',
    ]
