import os
import requests
import uuid
import shutil

import defaults
from eThread import EThread


class ENode:
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

        # parted files will reside in this folder, once
        # completed, the files will be concatenated.
        self.file_name = self.url.split('/')[-1]
        self.file_name = self.file_name.split('?')[0]
        self.folder_name = self.file_name + ".parts"

        # save_location is the parent folder location
        if 'save_location' in kwargs:
            self.save_location = kwargs['save_location']
        else:
            self.save_location = defaults.save_location

        # download location is where the threads saves the part files
        self.download_location = os.path.join(self.save_location,
                                              self.folder_name)

        self.make_ready()

    def make_ready(self):
        '''
        All the data to be set and configs to be loaded required to
        make the download object fully functional, is done here.
        At this point, the ENode should be independent, it has acquired
        all the data from external sources.
        '''
        if not os.path.exists(self.download_location):
            os.makedirs(self.download_location)

        # an initial request is required to download the headers for
        # the file. This information will be used to distribute tasks between
        # the multiple threads.
        headers = requests.head(self.url)
        if headers.status_code == 200:
            headers = headers.headers

        self.file_size = long(headers['content-length'])
        accept_ranges = headers['accept-ranges']

        # compute the chunk size per thread
        self.download_headers = []
        bytes_per_thread = self.file_size / self.thread_count
        bytes_assigned = 0

        for thread in range(self.thread_count):
            range_start = bytes_assigned
            range_end = range_start + bytes_per_thread - 1

            bytes_assigned += bytes_per_thread

            self.download_headers.append({
                'accept-ranges': accept_ranges,
                'range-start': range_start,
                'range-end': range_end,
            })

        # blindly set range_end as self.file_size, this will compensate for
        # any bytes left behind
        self.download_headers[-1]['range-end'] = self.file_size

        # download_thread will contain all the threads
        self.worker_threads = []

    def start_threads(self):
        for thread in range(self.thread_count):
            new_thread = EThread(
                threadID=thread,
                threadUUID=uuid.uuid4(),
                url=self.url,
                header=self.download_headers[thread],
                file_name=self.file_name,
                download_location=self.download_location,
            )
            new_thread.start()
            self.worker_threads.append(new_thread)

        for thread in self.worker_threads:
            thread.join()

        self.post_download()

    def pause_threads(self):
        '''
        Threads will be paused, but will be present in memory
        '''
        pass

    def kill_threads(self):
        '''
        Threads will be killed
        '''
        #for thread in self.worker_threads:

        pass

    def get_current_status(self):
        status = {
            'status': 'online'
        }
        return status

    def post_download(self):
        '''
        This method will join the different file parts
        '''
        download_file_name = os.path.join(self.save_location, self.file_name)
        new_file = open(download_file_name, 'w')
        new_file.close()
        new_file = open(download_file_name, 'a')
        for thread in self.worker_threads:
            part_file_content = open(thread.file_name, 'r')
            shutil.copyfileobj(part_file_content, new_file)
            part_file_content.close()
        shutil.rmtree(self.download_location)
        new_file.close()
