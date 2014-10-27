import json
import os
from shutil import rmtree

from eNode import ENode


class EManager:
    def __init__(self):
        self.eNodes = []

    def main(self):
        pass

    def overall_status(self):
        '''
        Returns a JSON containing data about all ENodes
        '''
        payload = {}

        eNodes_data = []
        for eNode in self.eNodes:
            eNodes_data.append({
                'name': eNode.file_name,
                'size': eNode.file_size,
                'url': eNode.url,
                'thread_count': eNode.thread_count,
                'downloaded': eNode.data_downloaded(),
            })

        payload['eNodes'] = eNodes_data
        return json.dumps(payload)

    def create_eNode(self, payload):
        '''
        Spawn a new node. payload must be a dict with atleast a url.
        payload can also have optional data such as:
            thread_count, verbosity, save_location
        '''
        new_eNode = ENode(payload)
        if not new_eNode.invalid_url:
            # eNode was unable to retrieve the file header
            self.eNodes.append(new_eNode)
            new_eNode.start()

    def start_eNode(self, eNode):
        '''
        Restart a download. The download procedures starts automatically
        upon creation
        '''
        eNode.start_threads()

    def stop_eNode(self, eNode):
        '''
        Threads stopped safely
        '''
        eNode.stop_threads()

    def delete_eNode(self, eNode):
        '''
        Threads killed, but download data still remains
        '''
        eNode.stop_threads()
        eNode_index = self.eNodes.index(eNode)
        self.eNodes.pop(eNode_index)
        del eNode

    def delete_eNode_with_data(self, eNode):
        '''
        Threads killed, downloaded data deleted
        '''
        self.delete_eNode(eNode)

        # Remove compiled file if its exists
        downloaded_filename = eNode.get_downloaded_filename()
        if os.path.exists(downloaded_filename):
            os.remove(downloaded_filename)

        # Remove group folder containing all the parts if it exists
        group_foldername = eNode.get_group_foldername()
        if os.path.exists(group_foldername):
            rmtree(group_foldername)

    def start_all_eNodes(self):
        '''
        Attempts to start all eNodes irrespective of their states
        '''
        for eNode in self.eNodes:
            self.start_eNode(eNode)

    def pause_all_eNodes(self):
        '''
        Attempts to pause all eNodes irrespective of their states
        '''
        for eNode in self.eNodes:
            self.pause_eNode(eNode)

    def delete_all_eNodes(self):
        '''
        Attempts to delete all eNodes irrespective of their states
        '''
        for eNode in self.eNodes:
            self.delete_eNode(eNode)

    def delete_all_eNodes_with_data(self):
        '''
        Attempts to delete all eNodes and downloaded data
        irrespective of their states
        '''
        for eNode in self.eNodes:
            self.delete_eNode_with_data(eNode)
