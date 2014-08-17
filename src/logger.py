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
