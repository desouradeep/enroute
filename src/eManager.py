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

    def overall_status(self):
        return "%d online" % self.id

