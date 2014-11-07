import requests
import threading
import os

from contextlib import closing
from datetime import datetime


class EThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super(EThread, self).__init__()
        self._stop = threading.Event()

        self.threadID = kwargs['threadID']
        self.threadUUID = kwargs['threadUUID']
        self.url = kwargs['url']
        self.download_header = kwargs['header']
        self.download_location = kwargs['download_location']

        self.file_name = kwargs['file_name'] + '.part' + str(self.threadID)
        self.file_name = os.path.join(self.download_location, self.file_name)

        self.range_start = self.download_header['range-start']
        self.range_end = self.download_header['range-end']
        self.part_size = self.download_header['part-size']

        self.data_downloaded = 0

    def stop(self):
        '''
        Initiated by a stop request from the client
        '''
        self._stop.set()

    def stopped(self):
        '''
        Returns stopped status
        '''
        return self._stop.isSet()

    def running(self):
        '''
        Returns running status
        '''
        return not self.stopped()

    def download(self, part_file, chunk_size, headers):
        self.now = datetime.now()
        with closing(
            requests.get(self.url, stream=True, headers=headers)
        ) as request:
            with open(self.file_name, 'wb') as part_file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    print datetime.now() - self.now
                    self.now = datetime.now()
                    if chunk:
                        part_file.write(chunk)
                        part_file.flush()
                        os.fsync(part_file.fileno())
                        self.data_downloaded += chunk_size

                        # stop request initiated by client
                        if self.stopped():
                            break

    def download_completed(self):
        '''
        Determines if the thread has done its work
        Returns True if self.part_size matches the downloaded file size
        '''
        if os.path.exists(self.file_name):
            return self.part_size == os.path.getsize(self.file_name)
        else:
            return False

    def data_downloaded_physically(self):
        '''
        Returns the amount of data already downloaded
        '''
        if os.path.exists(self.file_name):
            return os.path.getsize(self.file_name)
        else:
            return 0

    def percentage_downloaded(self):
        '''
        Returns the percentage of data downloaded
        '''
        data_downloaded = float(self.data_downloaded_physically())
        percentage = data_downloaded / self.part_size * 100

        return percentage

    def run(self):
        print "Thread %s started" % self.threadID

        #self.range_start = str(self.data_downloaded_physically())
        headers = {
            'Range': 'bytes=%s-%s' % (self.range_start, self.range_end)
        }

        # set chunk size to 5KB, the program will dump this into disk
        # according to chunk_size at a time, making the space complexity
        # independent of the file size
        chunk_size = 1024 * 5

        # create file, in case it doesn't exist
        part_file = open(self.file_name, 'a')
        part_file.close()

        self.download(part_file, chunk_size, headers)
