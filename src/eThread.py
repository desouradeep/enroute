import requests
import threading
import os

from contextlib import closing


class EThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)

        self.threadID = kwargs['threadID']
        self.threadUUID = kwargs['threadUUID']
        self.url = kwargs['url']
        self.download_header = kwargs['header']
        self.save_location = kwargs['save_location']

        self.filename = kwargs['filename'] + '.part' + str(self.threadID)
        self.filename = os.path.join(self.save_location, self.filename)

        self.accept_ranges = self.download_header['accept-ranges']
        self.range_start = self.download_header['range-start']
        self.range_end = self.download_header['range-end']
        self.part_size = self.range_end - self.range_start

    def download(self, part_file, chunk_size, data_downloaded, headers):
        with closing(
            requests.get(self.url, stream=True, headers=headers)
        ) as request:
            with open(self.filename, 'wb') as part_file:
                for chunk in request.iter_content(chunk_size=chunk_size):
                    if chunk:
                        part_file.write(chunk)
                        part_file.flush()
                        os.fsync(part_file.fileno())
                        data_downloaded += chunk_size

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
        part_file = open(self.filename, 'a')
        part_file.close()

        data_downloaded = 0

        self.download(part_file, chunk_size, data_downloaded, headers)
