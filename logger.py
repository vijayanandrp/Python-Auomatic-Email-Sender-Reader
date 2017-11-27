# -*- coding: utf-8 -*-

import logging
from config import log_file


class Logger(object):
    """ module for logging the executions and statements """

    @staticmethod
    def defaults(name, logfile=log_file, debug_level='DEBUG', output_stream=False):
        """ default configuration settings in the method """
        if debug_level is "INFO":
            debug_level = logging.INFO
        elif debug_level is "DEBUG":
            debug_level = logging.DEBUG
        else:
            debug_level = logging.INFO

        # log file configuration
        logging.basicConfig(
                level=debug_level,
                filename=logfile,
                filemode='a',
                format='[%(asctime)s] - %(name)s - %(levelname)s - %(message)s',
                datefmt='%d/%b/%Y %H:%M:%S')

        if type(output_stream) is bool and output_stream:
            # console output
            console = logging.StreamHandler()
            console.setLevel(debug_level)
            console.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
            logging.getLogger('').addHandler(console)
        return logging.getLogger("{}".format(name))
