#! /usr/bin/env python
# coding=utf8

import logging
import os
import safestore.db.db_provider as dbprovider
import sys

from dropbox import client, rest
from dropbox.rest import ErrorResponse
import ConfigParser

config = ConfigParser.ConfigParser()
HERE = os.path.abspath(os.path.dirname(__file__))
config.read(os.path.join(HERE, '../configuration/ACCOUNTS.INI'))

CLIENT_ID = config.get('DROPBOX', 'CLIENT_ID')
CLIENT_SECRET = config.get('DROPBOX', 'CLIENT_SECRET')
AUTHORIZE_URI = config.get('DROPBOX', 'authorize_uri')
TOKEN_URI = config.get('DROPBOX', 'token_uri')
CODE_URI = config.get('DROPBOX', 'code_uri')
TEST = config.getboolean('MAIN', 'TEST')
if TEST:
    TEST_TOKEN = config.get('DROPBOX', 'TEST_TOKEN')


class DBox():

    def __init__(self):
        self.logger = logging.getLogger('dbox')
        db = dbprovider.DB()
        self.api_client = None
        if TEST:
            access_token = TEST_TOKEN
        else:
            access_token = db.get_provider_token('dropbox')
        if access_token is None:
            flow = client.DropboxOAuth2FlowNoRedirect(CLIENT_ID, CLIENT_SECRET)
            authorize_url = flow.start()
            sys.stdout.write(
                "0. Make sure you are logged in at  your account.\n")
            sys.stdout.write("1. Go to: " + authorize_url + "\n")
            sys.stdout.write(
                "2. Click \"Allow\" (you might have to log in first).\n")
            sys.stdout.write("3. Copy the authorization code.\n")
            code = raw_input("Enter the authorization code here: ").strip()
            try:
                access_token, user_id = flow.finish(code)
                db.set_provider_token('dropbox', access_token)
                self.logger.info(
                    'Successful login with user %s' % str(user_id))
            except rest.ErrorResponse, e:
                self.logger.error('Error: %s\n' % str(e))
        self.api_client = client.DropboxClient(access_token)
        self.logger.info("Successful client connection")
        # Dropbox tokens are valid forever
        db.shutdown_database()

    def createDir(self, path):
        self.logger.debug("Create path:" + path)
        # DropBox automatically create parent folder in puts

    def put(self, data, path):
        self.logger.debug("Put path:" + path)
        self.api_client.put_file(path, data, overwrite=True)

    def get(self, path):
        self.logger.debug("Get path:" + path)
        try:
            f, metadata = self.api_client.get_file_and_metadata(path)
        except ErrorResponse:
            return None
        except Exception:
            self.logger.exception("get dbox.py error")
            return None
        return f.read()

    def delete(self, path):
        self.logger.debug("Delete path:" + path)
        self.api_client.file_delete(path)

    def listChildren(self, path):
        res = []
        try:
            for mfile in self.api_client.metadata(path, file_limit=25000)["contents"]:
                cut = mfile["path"].rfind('/')
                res.append(mfile["path"][cut + 1:])
        except ErrorResponse:
            self.logger.exception("listChildren error")
        return res

    def clean(self, path):
        self.logger.info("Clean " + path)
        files = self.api_client.metadata(path, file_limit=25000)["contents"]
        self.logger.debug("Will try to delete" + str(len(files)) + "files from dropbox")
        deleted_files = 0
        try:
            for mfile in files:
                self.logger.debug("deleting: " + mfile["path"])
                self.api_client.file_delete(mfile["path"])
                deleted_files += 1
        except ErrorResponse as e:
            self.logger.error(e)
            self.logger.error("failed after " + str(deleted_files) + " deletion")
        return deleted_files
        #self.api_client.file_delete(path)
        # 406 (Not Acceptable) status

    def clear(self):
        self.clean("/")

    def quota(self):
        """Returns the current free space in bytes in the Drive
        """
        return self.api_client.account_info()['quota_info']['quota']

    def getUserEmail(self):
        return self.api_client.account_info()['email']

    def getUserName(self):
        return self.api_client.account_info()['display_name']
