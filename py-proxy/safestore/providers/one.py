#! /usr/bin/env python
# coding=utf8

import logging
import os
import sys
import uuid
import safestore.handler.defines as defines
import safestore.db.db_provider as dbprovider
from onedrive import api_v5
from onedrive.api_v5 import DoesNotExists, ProtocolError
from httplib import BadStatusLine, ResponseNotReady
from ssl import SSLError
import requests
import ConfigParser



config = ConfigParser.ConfigParser()
HERE = os.path.abspath(os.path.dirname(__file__))
config.read(os.path.join(HERE, '../configuration/ACCOUNTS.INI'))


CLIENT_ID = config.get('ONEDRIVE','CLIENT_ID')
CLIENT_SECRET = config.get('ONEDRIVE','CLIENT_SECRET')
REDIRECT_URI = config.get('ONEDRIVE', 'REDIRECT_URI')
AUTHORIZE_URI = config.get('ONEDRIVE','AUTHORIZE_URI')
TOKEN_URI = config.get('ONEDRIVE','TOKEN_URI')
CODE_URI = config.get('ONEDRIVE','CODE_URI')

class ODrive():
    def __init__(self):
        self.logger = logging.getLogger('onedrive')
        db = dbprovider.DB()
        self.api_client = None
        self.api = self.setup_api()
        access_token  = db.get_provider_token('onedrive')
        refresh_token  = db.get_provider_refresh_token('onedrive')
        if access_token is None:
            authorize_url = self.api.auth_user_get_url()
            sys.stdout.write("1. Go to: " + authorize_url + "\n")
            sys.stdout.write("2. Click \"Allow\" (you might have to log in first).\n")
            sys.stdout.write("3. Copy the redirect url.\n")
            url = raw_input("Enter the authorization url here: ").strip()
            print self.api.auth_user_process_url(url)
            print self.api.auth_get_token()
            db.set_provider_token('onedrive',self.api.auth_access_token,self.api.auth_refresh_token)
        else:
            self.api.auth_access_token=access_token
            self.api.auth_refresh_token=refresh_token
        self.logger.info("Access token: "+ str(access_token))
        db.shutdown_database()

    @staticmethod
    def setup_api():
        """
        Initiates the onedrive API client.
        Returns:
            A configured api client
        """
        api = api_v5.OneDriveAPI()
        api.client_id=CLIENT_ID
        api.client_secret=CLIENT_SECRET
        api.auth_url_user=AUTHORIZE_URI
        api.auth_redirect_uri=REDIRECT_URI
        api.auth_scope=(api.auth_scope[0], api.auth_scope[1], api.auth_scope[2], 'wl.emails')
        return api

    def createDir(self,path):
        paths=path.split("/")
        parent_id='me/skydrive'
        if len(paths)>3:
            cut=path[0:-1].rfind('/')
            parent_id=self.api.resolve_path(path[:cut+1])
        self.api.mkdir(paths[-2],folder_id=parent_id)

    def listChildren(self,path):
        try:
            url=self.api.resolve_path(path)
            return [x['name'] for x in self.api.listdir(folder_id=url)]
        except DoesNotExists:
            self.logger.exception("listChildren error")
            return []


    def put(self, data, path):
        self.logger.debug("Put path:"+path)
        tmpfile_path=defines.TEMP_PATH + 'tmpfile-one' + str(uuid.uuid4())
        cut=path.rfind('/')
        path=path[cut+1:]
        api = self.setup_api()
        try:
            myfile = defines.temp_file_open(tmpfile_path)
            myfile.seek(0)
            myfile.write(data)
            myfile.seek(0)
            parent_id=api.resolve_path(path[:cut+1])
            api.put((path,myfile),folder_id=parent_id)
        except (ProtocolError,SSLError,BadStatusLine,ResponseNotReady) as e:
            #Try again
            print e
            self.put(data,path)
        finally:
            defines.temp_file_close(myfile)
            defines.temp_file_delete(tmpfile_path)

    def get(self,path):
        self.logger.debug("Get path:"+path)
        try:
            url=self.api.resolve_path(path)
            contents = self.api.get(url)
            return contents
        except DoesNotExists:
            return None
        except (ProtocolError,SSLError,BadStatusLine,ResponseNotReady):
            #Try again
            return self.get(path)

    def clean(self,path):
        self.logger.debug("Clean path:"+path)
        try:
            url=self.api.resolve_path(path)
            files=self.api.listdir(folder_id=url)
            for mfile in files:
                link=mfile['id']
                self.api.delete(link)
            if path!='/':
                self.api.delete(url)
        except DoesNotExists:
            return None
        except (ProtocolError,SSLError,BadStatusLine,ResponseNotReady),e:
            #Try again
            print "Error"+str(e)
            self.clean(path)

    def clear(self):
        self.clean("/")

    def delete(self,path):
        self.logger.debug("Delete path:"+path)
        try:
            url=self.api.resolve_path(path)
            self.api.delete(url)
        except DoesNotExists:
            return None
        except (ProtocolError,SSLError,BadStatusLine,ResponseNotReady):
            #Try again
            self.delete(path)

    def quota(self):
        """Returns the current free space in bytes in the Drive
        """
        try:
            return self.api.get_quota()[0]
        except (ProtocolError,SSLError,BadStatusLine,ResponseNotReady):
            #Try again
            return self.quota()

    def getUserEmail(self):
       return requests.get("https://apis.live.net/v5.0/me?access_token="+self.api.auth_access_token).json()['emails']['account']

    def getUserName(self):
        return requests.get("https://apis.live.net/v5.0/me?access_token="+self.api.auth_access_token).json()['name']
