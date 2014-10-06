import requests
import threading
import os

from contextlib import closing


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

        self.accept_ranges = self.download_header['accept-ranges']
        self.range_start = self.download_header['range-start']
        self.range_end = self.download_header['range-end']
        self.part_size = self.range_end - self.range_start

        self.data_downloaded = 0

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def download(self, part_file, chunk_size, headers):
        with closing(
            requests.get(self.url, stream=True, headers=headers)
        ) as request:
            with open(self.file_name, 'wb') as part_file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    if chunk:
                        part_file.write(chunk)
                        part_file.flush()
                        os.fsync(part_file.fileno())
                        self.data_downloaded += chunk_size

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

    def run(self):
        print "Thread %s started" % self.threadID
        headers = {
            'Range': '%s=%s-%s' % (self.accept_ranges, self.range_start,
                                   self.range_end)
        }

        # set chunk size to 5KB, the program will dump this into disk
        # according to chunk_size at a time, making the space complexity
        # independent of the file size
        chunk_size = 1024 * 5

        # create file, in case it doesn't exist
        part_file = open(self.file_name, 'a')
        part_file.close()

        self.download(part_file, chunk_size, headers)
