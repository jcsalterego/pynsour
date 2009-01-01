"""Configuration class

Read config file
"""
from yaml import load, dump

class Config:
    def __init__(self):
        pass

    def read(self, file_):
        data = yaml.load(file_)
        return data
