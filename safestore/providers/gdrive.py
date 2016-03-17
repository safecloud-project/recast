#! /usr/bin/env python
# coding=utf8

import httplib2
import safestore.db.db_provider as dbprovider
import safestore.handler.defines as defines

from apiclient.errors import HttpError
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import OAuth2Credentials
from oauth2client.client import AccessTokenCredentialsError
from oauth2client.service_account import ServiceAccountCredentials

from httplib import BadStatusLine, ResponseNotReady
import logging
import ConfigParser
from ssl import SSLError

config = ConfigParser.ConfigParser()
config.read('ACCOUNTS.INI')

CLIENT_ID = config.get('GDRIVE', 'CLIENT_ID')
CLIENT_SECRET = config.get('GDRIVE', 'CLIENT_SECRET')
SCOPE = config.get('GDRIVE', 'SCOPE')
REDIRECT_URI = config.get('GDRIVE', 'REDIRECT_URI')
AUTHORIZE_URI = config.get('GDRIVE', 'AUTHORIZE_URI')
TOKEN_URI = config.get('GDRIVE', 'TOKEN_URI')
CODE_URI = config.get('GDRIVE', 'CODE_URI')

TEST = config.getboolean('MAIN', 'TEST')
if TEST:
    SERVICE_ACCOUNT = config.get('GDRIVE', 'SERVICE_ACCOUNT')


class GDrive():

    def __init__(self):
        self.logger = logging.getLogger('gdrive')

        if False:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                SERVICE_ACCOUNT, scopes=SCOPE)
        else:
            credentials = self._login_account()
        http = httplib2.Http()
        http = credentials.authorize(http)
        self.drive_service = build('drive', 'v2', http=http)
        self.logger.info('Successful client connection')

    def _login_account(self):
        db = dbprovider.DB()
        access_token = db.get_provider_token('googledrive')
        self.logger.debug("GDrive: " + str(access_token))
        if access_token is None:
            # Run through the OAuth flow and retrieve credentials
            flow = OAuth2WebServerFlow(
                CLIENT_ID, CLIENT_SECRET, SCOPE, REDIRECT_URI)
            flow.params['access_type'] = 'offline'
            flow.params['approval_prompt'] = 'force'
            authorize_url = flow.step1_get_authorize_url()
            print 'Go to the following link in your browser: ' + authorize_url
            code = raw_input('Enter verification code: ').strip()
            #access_token= raw_input('Enter code: ').strip()
            credentials = flow.step2_exchange(code)
            access_token = credentials.access_token
            refresh_token = credentials.refresh_token
            token_expiry = credentials.token_expiry
            db.set_provider_token(
                'googledrive', access_token, refresh_token, token_expiry)
        else:
            access_token = str(access_token)
            refresh_token = db.get_provider_refresh_token('googledrive')
            token_expiry = db.get_provider_token_expiry('googledrive')
        db.shutdown_database()
        return OAuth2Credentials(access_token, CLIENT_ID, CLIENT_SECRET, refresh_token, token_expiry, TOKEN_URI, 'my-user-agent/1.0')

    def createDir(self, path):
        self.logger.debug("Create folder path:" + path)
        paths = path.split("/")
        # self.logger.debug(str(path),str(paths))
        parent_id = None
        if len(paths) > 3:
            cut = path[0:-1].rfind('/')
            parent_id = self.getFolder(path[:cut + 1])
        path = paths[-2]
        body = {
            'title': path,
            'mimeType': 'application/vnd.google-apps.folder',
        }
        # Set the parent folder.
        if parent_id:
            body['parents'] = [{'id': parent_id}]
        self.drive_service.files().insert(body=body).execute()

    def getFolder(self, path):

        paths = path.split("/")
        parent_id = None
        if len(paths) == 1 or paths[1] == '':
            paths = ['', '']
            parent_id = "root"
        print(paths)

        for i in range(1, len(paths) - 1):
            if parent_id:
                files = self.drive_service.files().list(q="'" + parent_id + "' in parents and title = '" +
                                                        paths[i] + "' and trashed = false and mimeType = 'application/vnd.google-apps.folder'").execute()
            else:
                files = self.drive_service.files().list(q="'root' in parents and title = '" +
                                                        paths[i] + "' and trashed = false and mimeType = 'application/vnd.google-apps.folder'").execute()
            if (len(files['items']) > 0):
                parent_id = files['items'][0]['id']
            else:
                return None
        return parent_id

    """
        Given a destination folder, return a tuple
        with the relative path and the parent id.
    """

    def _correct_dest_path(self, path):
        cut = path.rfind('/')

        """
            Some addresses do not have a folder and such the
            id must point to the root folder.
            On google drive root is an alias.
        """
        parent_id = "root"

        if(cut is not -1):
            parent_id = self.getFolder(path[:cut + 1])
            path = path[cut + 1:]

        return (path, parent_id)

    def put(self, data, path):
        self.logger.debug("Put path:" + path)
        (path, parent_id) = self._correct_dest_path(path)

        try:
            files = self.drive_service.files().list(q="'" + parent_id +
                                                    "' in parents and title = '" + path + "' and trashed = false").execute()

            if (len(files['items']) > 0):
                file_id = files['items'][0]['id']

                tmpfile_path = defines.TEMP_PATH + 'tmpfile-gdrive'
                myfile = defines.temp_file_open(tmpfile_path)
                myfile.seek(0)
                myfile.write(data)
                myfile.seek(0)
                media_body = MediaFileUpload(
                    tmpfile_path, mimetype='text/plain', resumable=True)
                body = {
                    'title': path,
                    'mimeType': 'text/plain',
                    'parents': [{'id': parent_id}]
                }
                self.drive_service.files().update(fileId=file_id, body=body,
                                                  newRevision=False, media_body=media_body).execute()
                defines.temp_file_close(myfile)
                defines.temp_file_delete(tmpfile_path)

            else:
                tmpfile_path = defines.TEMP_PATH + 'tmpfile-gdrive'
                myfile = defines.temp_file_open(tmpfile_path)
                myfile.seek(0)
                myfile.write(data)
                myfile.seek(0)
                media_body = MediaFileUpload(
                    tmpfile_path, mimetype='text/plain', resumable=True)
                body = {
                    'title': path,
                    'mimeType': 'text/plain',
                    'parents': [{'id': parent_id}]
                }

                self.drive_service.files().insert(body=body, media_body=media_body).execute()
                self.logger.debug("Exit put path:" + path)
                defines.temp_file_close(myfile)
                defines.temp_file_delete(tmpfile_path)
        except (HttpError, SSLError, BadStatusLine, ResponseNotReady):
            # Try again
            self.put(data, path)

    def get(self, path):
        try:
            self.logger.debug("Get path:" + path)
            (path, parent_id) = self._correct_dest_path(path)

            files = self.drive_service.files().list(q="'" + parent_id +
                                                    "' in parents and title = '" + path + "' and trashed = false").execute()
            if (len(files['items']) > 0):
                file_id = files['items'][0]['id']
                f = self.drive_service.files().get(fileId=file_id).execute()
                downloadUrl = f.get('downloadUrl')
                # If a download URL is provided in the file metadata, use it to make an
                # authorized request to fetch the file ontent. Set this content in the
                # data to return as the 'content' field. If there is no downloadUrl,
                # just set empty content.
                if downloadUrl:
                    resp, f['content'] = self.drive_service._http.request(
                        downloadUrl)
                else:
                    f['content'] = ''
                return f['content']
            else:
                return None
        except (HttpError, SSLError, BadStatusLine, ResponseNotReady):
            return self.get(path)

    def clean(self, path):
        try:
            self.logger.debug("Clean path:" + path)
            folder_id = self.getFolder(path)
            page_token = None
            while True:
                try:
                    param = {}
                    if page_token:
                        param['pageToken'] = page_token
                    children = self.drive_service.children().list(
                        folderId=folder_id, **param).execute()
                    for child in children.get('items', []):
                        self.drive_service.files().delete(
                            fileId=child['id']).execute()
                    page_token = children.get('nextPageToken')
                    if not page_token:
                        break
                except HttpError, error:
                    print 'An error occurred: %s' % error
                    break
            self.drive_service.files().delete(fileId=folder_id).execute()
        except (HttpError, SSLError, BadStatusLine), e:
            print e
            # self.clean()

    def listChildren(self, path):
        '''
        TODO
        Should return the list of file names that correspond to the regular expression passed as parameter.
        '''
        res = []
        folder_id = self.getFolder(path)
        if folder_id is None:
            return res
        page_token = None
        while True:
            try:
                param = {}
                if page_token:
                    param['pageToken'] = page_token
                children = self.drive_service.children().list(
                    folderId=folder_id, **param).execute()
                for child in children.get('items', []):
                    f = self.drive_service.files().get(
                        fileId=child['id']).execute()
                    res.append(f['title'])
                page_token = children.get('nextPageToken')
                if not page_token:
                    break
            except HttpError, error:
                print 'An error occurred: %s' % error
                break
        return res

    def delete(self, path):
        try:
            self.logger.debug("Delete path:" + path)
            cut = path.rfind('/')
            parent_id = self.getFolder(path[:cut + 1])
            path = path[cut + 1:]
            files = self.drive_service.files().list(q="'" + parent_id +
                                                    "' in parents and title = '" + path + "' and trashed = false").execute()
            if (len(files['items']) > 0):
                file_id = files['items'][0]['id']
                self.drive_service.files().delete(fileId=file_id).execute()
        except (HttpError, SSLError, BadStatusLine):
            self.delete(path)

    def quota(self):
        """Returns the current free space in bytes in the Drive
        """
        try:
            about = self.drive_service.about().get().execute()
            total = about['quotaBytesTotal']
            used = about['quotaBytesUsed']
            return int(total) - int(used)
        except (HttpError, SSLError, BadStatusLine):
            self.quota()

    def getUserEmail(self):
        about = self.drive_service.about().get().execute()
        return about['user']['emailAddress']

    def getUserName(self):
        about = self.drive_service.about().get().execute()
        return about['name']
