import os


class EnrouteLogger:
    def __init__(self, BASE_DIR_LOCATION, LOG_FILE_NAME, verbosity=2):
        self.LOG_FILE_LOCATION = os.path.join(BASE_DIR_LOCATION, LOG_FILE_NAME)
        if verbosity is None:
            self.verbosity = 2
        else:
            self.verbosity = verbosity

    def log_to_file(self, verbosity, header, message):
        '''
        Logs every message to file at LOG_FILE_LOCATION
        '''
        message = verbosity + ' : ' + header + ' \t ' + message
        log_file = open(self.LOG_FILE_LOCATION, 'a')
        log_file.write(message + '\n')
        log_file.close()

    def log(self, header, message, header_color, verbose_level):
        '''
        Recieves the parameters for a log, prints the log using
        if it is allowed by the verbosity level.
        Logs the message to a file at LOG_FILE_LOCATION
        '''
        DEFAULT = '\033[0m'
        default_color = DEFAULT
        if verbose_level <= self.verbosity:
            print header_color + header + default_color + '\t' + message

        verbosities = {
            1: 'DEBUG   ',
            2: 'INFO    ',
            3: 'NOTICE  ',
            4: 'WARNING ',
            5: 'ERROR   ',
            6: 'CRITICAL'
        }
        self.log_to_file(verbosities[verbose_level], header, message)

    def debug(self, header, message):
        '''
        Initiate a debug level log
        '''
        GREEN = '\033[92m'
        header_color = GREEN
        verbose_level = 1
        self.log(header.upper(), message, header_color, verbose_level)

    def info(self, header, message):
        '''
        Initiate an info level log
        '''
        BLUE = '\033[94m'
        header_color = BLUE
        verbose_level = 2
        self.log(header.upper(), message, header_color, verbose_level)

    def notice(self, header, message):
        '''
        Initiate a notice level log
        '''
        CYAN = "\033[0;36m"
        header_color = CYAN
        verbose_level = 3
        self.log(header.upper(), message, header_color, verbose_level)

    def warning(self, header, message):
        '''
        Initiate a warning level log
        '''
        PURPLE = '\033[95m'
        header_color = PURPLE
        verbose_level = 4
        self.log(header.upper(), message, header_color, verbose_level)

    def error(self, header, message):
        '''
        Initiate an error level log
        '''
        YELLOW = '\033[93m'
        header_color = YELLOW
        verbose_level = 5
        self.log(header.upper(), message, header_color, verbose_level)

    def critical(self, header, message):
        '''
        Initiate a critical level log
        '''
        RED = '\033[91m'
        header_color = RED
        verbose_level = 6
        self.log(header.upper(), message, header_color, verbose_level)
