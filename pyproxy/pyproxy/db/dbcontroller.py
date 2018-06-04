#! /usr/bin/env python
# coding=utf8
import sqlite3
import os
import datetime
import hashlib
import logging
import threading
import pyproxy.safestore.handler.defines as defines


FILE_SYSTEM_TABLE_CREATION='''CREATE TABLE FILE_SYSTEM(path TEXT PRIMARY KEY, type integer NOT NULL, timestamp timestamp NOT NULL, size integer NOT NULL)'''
BLOCK_LIST_PER_FILE_TABLE_CREATION='''CREATE TABLE BLOCK_LIST_PER_FILE(filename TEXT NOT NULL, offset integer NOT NULL, hash TEXT NOT NULL, blockid TEXT NOT NULL, PRIMARY KEY(filename,offset))'''
FILE_CHANGES_TABLE_CREATION='''CREATE TABLE FILE_CHANGES(id INTEGER PRIMARY KEY AUTOINCREMENT, operation integer NOT NULL, type integer NOT NULL, path TEXT NOT NULL, timestamp timestamp NOT NULL, processed integer NOT NULL, size integer NOT NULL)'''
PROVIDER_TOKENS_TABLE_CREATION='''CREATE TABLE PROVIDER_TOKENS(id TEXT PRIMARY KEY, token TEXT NOT NULL,refresh_token TEXT, token_expiry integer)'''
SETTINGS_TABLE_CREATION='''CREATE TABLE SETTINGS(setting integer PRIMARY KEY, value TEXT NOT NULL)'''

USER_LOGINS_TABLE_CREATION='''CREATE TABLE USER_LOGINS(provider_id TEXT PRIMARY KEY, type integer NOT NULL, login TEXT NOT NULL)'''


EMAIL_LOGINS_TABLE_CREATION='''CREATE TABLE EMAIL_LOGINS(login TEXT NOT NULL, id integer PRIMARY KEY AUTOINCREMENT, value TEXT NOT NULL, name TEXT NOT NULL)'''


BLOCK_IDS_TABLE_CREATION='''CREATE TABLE BLOCK_IDS(filename TEXT NOT NULL, offset integer NOT NULL, hash TEXT NOT NULL, blockid TEXT NOT NULL, PRIMARY KEY(filename,offset))'''
SYNC_TABLE_CREATION='''CREATE TABLE SYNC(path TEXT PRIMARY KEY)'''

DOWNLOAD_TABLE_CREATION='''CREATE TABLE DOWNLOAD(filename TEXT PRIMARY KEY, username TEXT NOT NULL)'''

class DBController:

    def __init__(self,myid=""):
        self.logger = logging.getLogger('machine'+str(myid))
        self.logger.info("Booting database")
        self.boot_database(myid)
        self.lock = threading.Lock()

    def boot_database(self,myid=""):

        #print "defines.DB_PATH:"+defines.DB_PATH
        path = defines.DB_PATH

        if not os.path.exists(path):
            self.logger.info("Creating database:"+str(path))

            self.conn = sqlite3.connect(path,detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread = False,isolation_level = "IMMEDIATE")
            #self.conn.text_factory = sqlite3.OptimizedUnicode
            # Create tables

            self.conn.execute(FILE_SYSTEM_TABLE_CREATION)
            self.conn.execute(BLOCK_LIST_PER_FILE_TABLE_CREATION)
            self.conn.execute(FILE_CHANGES_TABLE_CREATION)
            self.conn.execute(PROVIDER_TOKENS_TABLE_CREATION)
            self.conn.execute(SETTINGS_TABLE_CREATION)
            self.conn.execute(BLOCK_IDS_TABLE_CREATION)
            self.conn.execute(SYNC_TABLE_CREATION)
            self.conn.execute(EMAIL_LOGINS_TABLE_CREATION)
            self.conn.execute(USER_LOGINS_TABLE_CREATION)
            self.conn.execute(DOWNLOAD_TABLE_CREATION)

            self.conn.commit()


        else:
            self.logger.debug("Database exists, connecting")
            self.conn = sqlite3.connect(path,detect_types=sqlite3.PARSE_DECLTYPES,check_same_thread = False,isolation_level = "IMMEDIATE")

    def getConn(self):
        #print "getLock"
        self.lock.acquire()
        return self.conn

    def releaseConn(self):
        #print "releaseLock"
        self.lock.release()

