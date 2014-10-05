import requests

import defaults


class EObject:
    def __init__(self, *args, **kwargs):
        self.proceed = True

        # set minimum data required to get the ground running
        if 'url' in kwargs:
            self.url = kwargs['url']

        if 'thread_count' in kwargs:
            self.thread_count = kwargs['thread_count']
        else:
            # set default number of threads
            self.thread_count = defaults.thread_count

        if 'verbosity' in kwargs:
            self.verbosity = kwargs['verbosity']
        else:
            # set default verbosity level
            self.verbosity = defaults.verbosity

        self.make_ready()

    def make_ready(self):
        '''
        All the data to be set and configs to be loaded required to
        make the download object fully functional, is done here.
        At this point, the EObject should be independent, it has acquired
        all the data from external sources.
        '''
        # parted files will reside in this folder, once
        # completed, the files will be concatenated.
        self.folder_name = self.url.split('/')[-1]

        # an initial request is required to download the headers for
        # the file. This information will be used to distribute tasks between
        # the multiple threads.
        headers = requests.head(self.url)
        if headers.status_code == 200:
            headers = headers.headers

        self.file_size = long(headers['content-length'])

        # compute the chunk size per thread
        self.download_headers = []
        bytes_per_thread = self.file_size / self.thread_count
        bytes_assigned = 0

        for thread in range(self.thread_count):
            range_start = bytes_assigned
            range_end = range_start + bytes_per_thread - 1

            bytes_assigned += bytes_per_thread

            self.download_headers.append({
                'range-start': range_start,
                'range-end': range_end,
            })

        # blindly set range_end as self.file_size, this will compensate for
        # any bytes left behind
        self.download_headers[-1]['range-end'] = self.file_size

        # download_thread will contain all the threads
        self.download_threads = []
