#!/usr/bin/env python2
# Script to clean the database for the shareasecret app
# should be placed in a cron to be run nightly
# preferable run by the user who owns the app

from time import time
from os.path import realpath, dirname
import sqlite3


# function to delete rows where timestamp is
# older than a week
def cleandb():
    db = sqlite3.connect(dirname(realpath(__file__)) + '/secret.db')
    db.execute('DELETE FROM secrets WHERE timestamp < ?',
               [time() - 604800])
    db.commit()
    db.close()

if __name__ == '__main__':
    cleandb()
