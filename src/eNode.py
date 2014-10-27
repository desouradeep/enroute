import os
import requests
import uuid
import shutil
import threading

import defaults
from eThread import EThread


class ENode(threading.Thread):
    def __init__(self, kwargs):
        super(ENode, self).__init__()

        self.proceed = True

        # set minimum data required to hit the ground running
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

        # this becomes True if a request to the file header responds with
        # a non 200 status code
        self.invalid_url = False

        self.make_ready()

    def fetch_request_head(self):
        '''
        an initial request is required to download the headers for
        the file. This information will be used to distribute tasks between
        the multiple threads.
        '''
        try:
            request_headers = requests.head(self.url)
            if request_headers.status_code == 200:
                headers = request_headers.headers
                return headers
            else:
                return "invalid-url"
        except:
            return "invalid-url"

    def make_ready(self):
        '''
        All the data to be set and configs to be loaded required to
        make the download object fully functional, is done here.
        At this point, the ENode should be independent, it has acquired
        all the data from external sources.
        '''
        if not os.path.exists(self.download_location):
            os.makedirs(self.download_location)

        headers = self.fetch_request_head()
        if headers == 'invalid-url':
            self.invalid_url = True
            return

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
                'part-size': bytes_per_thread,
            })

        # blindly set range_end as self.file_size, this will compensate for
        # any bytes left behind
        last_thread_part_size = self.download_headers[-1]['range-end']
        bytes_remaining = self.file_size - last_thread_part_size - 1
        self.download_headers[-1]['range-end'] = self.file_size
        self.download_headers[-1]['part-size'] += bytes_remaining

        # worker_threads will contain all the threads
        self.worker_threads = []

        # This becomes True when stop request is initiated
        self.stop_downloading = False

        # Unique ID for the eNode
        self.uuid = str(uuid.uuid4())

    def run(self):
        print "eNode for %s started" % self.file_name
        download_ready = False
        compile_failure = False

        if self.download_completed():
            if self.data_compiled():
                download_ready = True
            else:
                compile_result = self.compile_data()
                if compile_result == 'success':
                    download_ready = True
                elif compile_result == 'failure':
                    compile_failure = True
            print "download_ready : %s" % download_ready
            print "compile_failure: %s" % compile_failure

        else:
            self.start_threads()

    def start_threads(self):
        '''
        Start off all the threads, intelligently handle start as well as
        resume events
        '''
        for thread in range(self.thread_count):
            new_thread = EThread(
                threadID=thread+1,
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

        self.compile_data()

    def download_completed(self):
        '''
        Determines if the file is downloaded
        '''
        complete = False

        if self.worker_threads:
            existing_thread_completed = 0
            for thread in self.worker_threads:
                if thread.download_completed():
                    existing_thread_completed += 1
            if existing_thread_completed == self.thread_count:
                complete = True
        else:
            # if none of the worker threads exists, compare the original
            # file size with the downloaded file sizes
            total_file_size = self.data_downloaded()

            if total_file_size == self.file_size:
                complete = True

        return complete

    def downloaded_file_size(self):
        '''
        Returns the size of the downloaded file
        '''
        data_downloaded = 0
        path_exists = os.path.exists(self.get_downloaded_filename())
        if path_exists:
            data_downloaded = long(os.path.getsize(
                self.get_downloaded_filename()))
        return path_exists, data_downloaded

    def data_downloaded(self):
        '''
        Returns the amount of collective data downloaded by each thread
        '''
        download_file_path, data_downloaded = self.downloaded_file_size()

        # check if the downloaded file itself is present
        if not download_file_path:
            for part in range(1, self.thread_count+1):
                # partfile_name is the physical address of the part file
                partfile_name = os.path.join(self.download_location) + \
                    '.part' + str(part)
                if os.path.exists(partfile_name):
                    partfile_size = os.path.getsize(partfile_name)
                    data_downloaded += long(partfile_size)

        return data_downloaded

    def percentage_downloaded(self):
        '''
        Return the percentage of the entire data downloaded
        '''
        downloaded_file_size = float(self.downloaded_file_size()[1])
        percentage = downloaded_file_size / self.file_size * 100
        return percentage

    def data_compiled(self):
        '''
        Check if the downloaded file exists and is of full size
        '''
        download_file_size = self.downloaded_file_size()[1]
        return self.file_size == download_file_size

    def stop_threads(self):
        '''
        Stop all the eThreads safely
        '''
        self.stop_downloading = True
        for thread in self.worker_threads:
            thread.stop()

    def get_current_status(self):
        '''
        Return detailed status about the eNode and all the threads
        '''
        thread_status = []

        eNode_status = {
            'uuid': self.uuid,
            'url': self.url,
            'thread_count': self.thread_count,
            'file_name': self.file_name,
            'file_location': self.get_downloaded_filename(),
            'group_foldername': self.get_group_foldername(),
            'file_size': self.file_size,
            'percentage_downloaded': self.percentage_downloaded(),
            'thread_status': thread_status,
            'stop_downloading': self.stop_downloading,
        }

        for thread in self.worker_threads:
            thread_status.append({
                'uuid': thread.threadUUID,
                'part_name': thread.file_name,
                'part_size': thread.part_size,
                'data_downloaded': thread.data_downloaded,
                'running': thread.running(),
                'download_completed': thread.download_completed,
                'percentage_downloaded': thread.percentage_downloaded,
            })

        return eNode_status

    def get_downloaded_filename(self):
        '''
        Get absolute location of the file being downloaded
        '''
        return os.path.join(self.save_location, self.file_name)

    def get_group_foldername(self):
        '''
        Get absolute location of the folder in which the downloaded parts
        are being stored
        '''
        return os.path.join(self.download_location)

    def compile_data(self):
        '''
        This method will join the different file parts
        '''
        print "Attempting to compile data"
        if self.download_completed():
            download_file_name = self.get_downloaded_filename()
            new_file = open(download_file_name, 'w')
            new_file.close()
            new_file = open(download_file_name, 'a')
            for thread in self.worker_threads:
                part_file_content = open(thread.file_name, 'r')
                # copy the file by chunks
                shutil.copyfileobj(part_file_content, new_file)
                part_file_content.close()
            shutil.rmtree(self.download_location)
            new_file.close()
            return "success"
        else:
            return "failure"
