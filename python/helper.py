import configparser
import os


def config(cat, param):
    cnf = configparser.ConfigParser()
    cnf.read(os.path.dirname(os.path.realpath(__file__)) + '/config.ini')
    return str(cnf.get(cat, param))
