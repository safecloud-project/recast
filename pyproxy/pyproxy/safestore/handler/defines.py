#! /usr/bin/env python
# coding=utf8

from os.path import expanduser
import os.path
from os import sep as PATH_SEPARATOR
import time
import thread
import logging


# Daemon
# number of iterations before getting remote changes
MAX_ITERS = 2

# OPERATION
ADD = 1
REM = 2
MOD = 3
MOV = 4
RENAME = 5

PATH_SEPARATOR = PATH_SEPARATOR

# OBJECT TYPE
FOLDER_TYPE = 90
FILE_TYPE = 91

BLOCKSIZE = 10 * 1024 * 1024  # 1MB

# WATCHDOG PROCESSED STATUS
NOT_PROC = 0
PROC = 1
REPEAT = 1

# SAFE Status
NOT_SYNCING = 0
SYNCING = 1
OFFLINE = 2

# changes type definition
#{ [string path : TYPE : OP] }
HOME_DIR = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../"))
APP_DIR = HOME_DIR
DB_PATH = os.path.join(APP_DIR, "data.db")
APP_DIR_SEP = os.path.join(APP_DIR, PATH_SEPARATOR)
TEMP_PATH = "/tmp/"  # APP_DIR

# APPLICATION SETTINGS
MACHINE_ID = 500
DATA_FOLDER = 501
PROVIDER_IDS = 502
LOCAL_PROVIDER_FOLDER = 503
MAIL_PROVIDER_IDS = 504
DATA_PROVIDER_IDS = 505
LOGIN_ID = 506
PASS_ID = 507
TOKEN_ID = 508

MAIL_PROVIDER = 1
DATA_PROVIDER = 2

OS_OPS = True


MAIL_SUBJECT_ID = "SCLOUD 32"
SHARE_DIR = "SHARE_SAFE"
SHARE_USER_EXISTS = 700
SHARE_NOT_FOUND = 404
SHARE_OK = 200
SHARE_EMAILS_DO_NOT_MATCH = 701

SAFECLOUD_DIR = "/SafeCloud/"
METADATA_DIR = SAFECLOUD_DIR + "metadata/"
TREES_DIR = METADATA_DIR + "trees/"
CHANGES_DIR = METADATA_DIR + "changes/"
BLOCKS_DIR = SAFECLOUD_DIR + "blocks/"

# Wizard constants
DROPBOX = "dropbox"
GDRIVE = "googledrive"
GMAIL = "gmail"
OUTLOOK = "outlook"
ONEDRIVE = "onedrive"
YAHOO = "yahoo"

# Retry Sleep for provider and OS failures
PSLEEP = 5
PERROR = 0
OSSLEEP = 5
OSERROR = 0

safeDeamon = None


def osdep_path(path):
    return path.replace('/', os.sep)


def safe_path(path):
    return path.replace(os.sep, '/')


def path_leaf(path):
    head, tail = os.path.split(path)
    return tail or os.path.basename(head)

# Normalize fullpath for distinct OS
# Add / for folders


def normalize_path(path, watchfolder, f_type):
    # Get relative path
    # Normalize the path for distinct OSs put / in.
    res_path = os.path.relpath(safe_path(path), watchfolder)
    # all folder paths end with /
    if(f_type == FOLDER_TYPE and res_path[-1] != '/'):
        res_path = res_path + '/'

    return res_path


def denormalize_path(path, watchfolder):

    if(watchfolder[-1] != '/'):
        watchfolder = watchfolder + '/'

    return osdep_path(watchfolder + path)


# TODO: add more special characters
def special_file(file_name):
    return file_name.startswith('.')


# TODO: error will be a code and will affect what the system tray icon displays
def retry_provider_op():
    global PERROR, PSLEEP

    # Warning this must be called without concurrency...
    if(PERROR == 0):
        PERROR = 1
        # TODO: tray must have a warning telling that a provider error exists
    if safeDeamon != None and safeDeamon.shouldIstop():
        thread.exit()
    time.sleep(PSLEEP)

# TODO: error will be a code and will affect what the system tray icon displays


def provider_op_resumed():
    global PERROR
    if(PERROR == 1):
        PERROR = 0
        # Remove tray warning, sync is back


def retry_os_op():
    global OSERROR, OSSLEEP
    # Warning this must be called without concurrency...
    if(OSERROR == 0):
        OSERROR = 1
        # TODO: tray must have a warning telling that an I/O error exists

    if safeDeamon != None and safeDeamon.shouldIstop():
        thread.exit()
    time.sleep(OSSLEEP)


def os_op_resumed():
    global OSERROR
    if(OSERROR == 1):
        OSERROR = 0
        # Remove tray warning, sync is back


def temp_file_open(path):
    f = open(path, "wb+")
    return f


def temp_file_close(filed):
    filed.close()


def temp_file_delete(path):
    os.remove(path)

'''
Log level
'''

TRACE_LEVEL_NUM = 9
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")


def trace(self, message, *args, **kws):
    # Yes, logger takes its '*args' as 'args'.
    self._log(TRACE_LEVEL_NUM, message, args, **kws)
logging.Logger.trace = trace

'''
Stats variables
'''
UP_TO_DATE = "Up to date"
OFFLINE_MSG = "Currently offline"
PAUSE = "Pause Syncing"
RESUME = "Resume Syncing"
