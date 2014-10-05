from argparse import ArgumentParser
import os
import requests

from logger import EnrouteLogger


class Enroute:
    def __init__(self, BASE_DIR_LOCATION, args):
        self.URL = args.url
        self.thread_count = args.threads
        self.verbosity = args.verbosity

        # Initiate EnrouteLogger as elog
        LOG_FILE_NAME = 'enroute.log'
        self.elog = EnrouteLogger(BASE_DIR_LOCATION, LOG_FILE_NAME)

    def main(self):
        pass

if __name__ == '__main__':
    # Initiate BASE DIRECTORY
    BASE_DIR_NAME = '.enroute'
    HOME_DIR_LOCATION = os.path.expanduser('~')
    BASE_DIR_LOCATION = os.path.join(HOME_DIR_LOCATION, BASE_DIR_NAME)

    # creating BASE DIRECTORY if not present
    if not os.path.exists(BASE_DIR_LOCATION):
        os.makedirs(BASE_DIR_LOCATION)

    parser = ArgumentParser(description='enroute: download files the\
                                         multithreading way')

    parser.add_argument('url',
                        help="download URL",
                        type=str,
                        action='store')

    default_threads = 5
    parser.add_argument('-t', '--threads',
                        help="number of threads used to download the file\
                              default %d threads" % (default_threads),
                        action='store',
                        type=int,
                        default=default_threads)

    parser.add_argument('-v', '--verbosity',
                        help="turn on verbosity",
                        action="store_true",
                        default=False)

    args = parser.parse_args()

    enrouter = Enroute(BASE_DIR_LOCATION, args)
    enrouter.main()
