from argparse import ArgumentParser
import os

from eNode import ENode
from logger import EnrouteLogger


class EManager:
    def __init__(self):
        self.eNodes = []
        self.id = 1

    def main(self):
        pass

    def create_eNode(self, payload):
        '''
        Spawn a new node. payload must be a dict with atleast a url.
        payload can also have optional data such as:
            thread_count, verbosity, save_location
        '''
        new_eNode = ENode(payload)
        return new_eNode

    def start_eNode(self, eNode):
        '''
        Start or Restart a download
        '''
        eNode.initiate_threads()

    def pause_eNode(self, eNode):
        '''
        Threads paused, but remain in memory
        '''
        eNode.pause_threads()

    def delete_eNode(self, eNode):
        '''
        Threads killed, but download data still remains
        '''
        eNode.kill_threads()
        del eNode

    def delete_eNode_with_data(self, eNode):
        '''
        Threads killed, downloaded data deleted
        '''
        self.delete_eNode(eNode)
        # TODO: code to delete downloaded files

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

    def overall_status(self):
        return "%d online" % self.id
