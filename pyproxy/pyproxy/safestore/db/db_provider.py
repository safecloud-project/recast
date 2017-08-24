#! /usr/bin/env python
# coding=utf8
import datetime
import hashlib
import logging
from dbcontroller import DBController
import pyproxy.safestore.handler.defines as defines

class DB:
    dbcontroller = None

    def __init__(self,myid=""):
        self.logger = logging.getLogger('machine'+str(myid))
        self.logger.info("Booting database")
        self.boot_database(myid)


    def boot_database(self,myid=""):
        if DB.dbcontroller is None:
          DB.dbcontroller = DBController(myid)

    def get_machine_id(self):
        return self.settings_getter(defines.MACHINE_ID)

    def set_machine_id(self,m_id):
        self.settings_setter(defines.MACHINE_ID,m_id)

    def set_providers_list(self,lst):
        self.settings_setter(defines.PROVIDER_IDS,lst)

    def get_providers_list(self):
        return self.settings_getter(defines.PROVIDER_IDS)

    def get_data_folder(self):
        return self.settings_getter(defines.DATA_FOLDER)

    def set_data_folder(self,path):
        self.settings_setter(defines.DATA_FOLDER,path)

    def get_local_provider_folder(self):
        return self.settings_getter(defines.LOCAL_PROVIDER_FOLDER)

    def set_local_provider_folder(self,path):
        self.settings_setter(defines.LOCAL_PROVIDER_FOLDER,path)

    def set_login(self,login):
        self.settings_setter(defines.LOGIN_ID,login)

    def set_pass(self,password):
        self.settings_setter(defines.PASS_ID,password)

    def get_login(self):
        return self.settings_getter(defines.LOGIN_ID)

    def set_token(self,token):
        self.settings_setter(defines.TOKEN_ID,token)

    def get_token(self):
        return self.settings_getter(defines.TOKEN_ID)

    def get_pass(self):
        return self.settings_getter(defines.PASS_ID)

    def settings_setter(self,setting,value):
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into SETTINGS values(?,?)', (setting,value) )
        conn.commit()
        DB.dbcontroller.releaseConn()

    def settings_getter(self,setting):
        try:
          conn = DB.dbcontroller.getConn()
          res = conn.execute('select value from SETTINGS where setting=?', (setting,)).fetchone()[0]
          DB.dbcontroller.releaseConn()
          return res
        except:
          DB.dbcontroller.releaseConn()
          return None

    def add_file_to_download(self,filename,username):
        """
        insert a file into download table
        """
        conn = DB.dbcontroller.getConn()
        res=conn.execute('select * from DOWNLOAD where filename= ?', (filename,))
        if(len(res.fetchall())==0):
            conn.execute('insert into DOWNLOAD(filename,username) values(?,?)', (filename,username))
        DB.dbcontroller.releaseConn()

    def get_download_row(self,rowid):
        """
        Returns rwo nr x for download table
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from DOWNLOAD where id= ?', (rowid+1,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def get_download_rows(self):
        """
        Returns all rows from download table
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from DOWNLOAD').fetchall()
        DB.dbcontroller.releaseConn()
        return res

    def get_number_download_rows(self):
        """
        Returns the number of rows for download table
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select count(*) from DOWNLOAD').fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def remove_download_file(self,filename):
        """
        Removes a download row
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from DOWNLOAD where filename=?', (filename,))
        DB.dbcontroller.releaseConn()

    def clean_download_files(self):
        """
        Cleans the downloads table
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from DOWNLOAD ')
        DB.dbcontroller.releaseConn()


    def set_mail_provider_login(self,providerid,login):
        """
        inserts a mail provider info
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert into USER_LOGINS(provider_id,type,login) values(?,?,?)', (providerid,defines.MAIL_PROVIDER,login))
        DB.dbcontroller.releaseConn()


    def get_mail_providers_logins(self):
        """
        Returns the login and id for mail providers fr this user
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from USER_LOGINS where type= ?', (defines.MAIL_PROVIDER,)).fetchall()
        DB.dbcontroller.releaseConn()
        return res

    def set_data_provider_login(self,providerid,login):
        """
         inserts a data provider info
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert into USER_LOGINS(provider_id,type,login) values(?,?,?)', (providerid,defines.DATA_PROVIDER,login))
        DB.dbcontroller.releaseConn()


    def get_data_providers_logins(self):
        """
        Returns the login and id for data providers for this user
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from USER_LOGINS where type= ?', (defines.DATA_PROVIDER,)).fetchall()
        DB.dbcontroller.releaseConn()
        return res

    def get_provider_login(self,providerString):
        """
        Returns the login and id for data providers for this user
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from USER_LOGINS where provider_id= ?', (providerString,)).fetchone()
        DB.dbcontroller.releaseConn()
        print str(res)
        return res[2]


    #TODO in the future replace the string with "," for distinct addresses in specific db rows?
    def get_mail_addresses(self,login):
        """
        Returns the login and emial addresses separated by ","
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from EMAIL_LOGINS where login= ?', (login,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def get_mail_row(self,rowid):
        """
        Returns the login and emial addresses separated by ","
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from EMAIL_LOGINS where id= ?', (rowid+1,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def get_number_rows(self):
        """
        Returns the number of rows for local user logins
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select count(*) from EMAIL_LOGINS').fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def set_mail_addresses(self,login,mails,name):
        """
        Inserts new login and corresponding email addresses searated by ","
        """
        conn = DB.dbcontroller.getConn()
        res=conn.execute('select * from EMAIL_LOGINS where login= ?', (login,))
        if(len(res.fetchall())==0):
            conn.execute('insert into EMAIL_LOGINS(login,value,name) values(?,?,?)', (login,mails,name))
        conn.commit()
        DB.dbcontroller.releaseConn()


    def shutdown_database(self):
        return


    def add_path(self,path,pathType,timestamp,size=0):
        """
        To be used to insert paths in the file system.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into FILE_SYSTEM values(?,?,?,?)', (path,pathType,timestamp,size))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def get_path(self,path):
        """
        Returns the path, path type and timestamp.
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from FILE_SYSTEM where path= ?', (path,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res


    def get_all_paths(self,batch_size=1000):
        """
        Returns all the paths, path type and timestamp in the filesystem.
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from FILE_SYSTEM').fetchall()
        #return self.lazy_generator(my_cursor.fetchmany,batch_size)
        DB.dbcontroller.releaseConn()
        return res

    def remove_path(self,path):
        """
        To be used to remove paths in the file system.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from FILE_SYSTEM where path=?', (path,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def add_block_to_file(self,filename,offset,block_hash,blockid):
        """
        Adds or updates the block_hash and offset for the given filename.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into BLOCK_LIST_PER_FILE values(?,?,?,?)', (filename,offset,block_hash,blockid))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def remove_block_from_file(self,filename,offset):
        """
        Removes _all_ blocks greater or equal than offset from the given file
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from BLOCK_LIST_PER_FILE where filename=? and offset>=?', (filename,offset,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def get_all_blocks_from_file(self,filename,batch_size=1000):
        """
        Retrieve all blocks from the given file
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from BLOCK_LIST_PER_FILE where filename=?', (filename,)).fetchall()
        DB.dbcontroller.releaseConn()
        return res
        #return self.lazy_generator(my_cursor.fetchmany,batch_size)

    def get_block_from_file(self,filename,offset):
        """
        Retrieve the blocks from the given file and offset
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from BLOCK_LIST_PER_FILE where filename=? and offset=?', (filename,offset,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def get_all_blocks_from_all_files(self,batch_size=1000):
        """
        Retrieve the blocks from the given file and offset
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from BLOCK_LIST_PER_FILE').fetchall()
        DB.dbcontroller.releaseConn()
        return res
        #return self.lazy_generator(my_cursor.fetchmany,batch_size)

    def FileSynced(self,path):
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into SYNC(path) values(?)', (path,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def isFileSynced(self,path):
        conn = DB.dbcontroller.getConn()
        result=conn.execute('select * from SYNC where path= ?', (path,)).fetchone()
        DB.dbcontroller.releaseConn()
        if(result==None):
          return False
        else:
          return True

    def cleanSyncDB(self):
        """
        Deletes all the SYNC entries.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from SYNC')
        conn.commit()
        DB.dbcontroller.releaseConn()

    def add_block_id(self,filename,offset,block_hash,blockid):
        """
        Adds or updates the block_hash and offset for the given filename.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into BLOCK_IDS values(?,?,?,?)', (filename,offset,block_hash,blockid))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def get_block_id(self,filename,offset):
        """
        Retrieve the blocks from the given file and offset
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from BLOCK_IDS where filename=? and offset=?', (filename,offset,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def get_all_block_ids_from_file(self,filename,batch_size=1000):
        """
        Retrieve all blocks from the given file
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from BLOCK_IDS where filename=?', (filename,)).fetchall()
        DB.dbcontroller.releaseConn()
        return res
        #return self.lazy_generator(my_cursor.fetchmany,batch_size)


    def cleanup_blockids(self):
        """
        Deletes all the SYNC entries.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from BLOCK_IDS')
        conn.commit()
        DB.dbcontroller.releaseConn()


    def watchdog_path_created(self,path, pathType,timestamp,size):
        conn = DB.dbcontroller.getConn()
        conn.execute('insert into FILE_CHANGES(operation,type,path,timestamp,processed,size) values(?,?,?,?,?,?)', (defines.ADD, pathType,path,timestamp,defines.NOT_PROC,size))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_path_modified(self,path, pathType,timestamp,size):
        conn = DB.dbcontroller.getConn()
        conn.execute('insert into FILE_CHANGES(operation,type,path,timestamp,processed,size) values(?,?,?,?,?,?)', (defines.MOD, pathType,path,timestamp,defines.NOT_PROC,size))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_path_deleted(self,path, pathType,timestamp,size):
        conn = DB.dbcontroller.getConn()
        conn.execute('insert into FILE_CHANGES(operation,type,path,timestamp,processed,size) values(?,?,?,?,?,?)', (defines.REM, pathType,path,timestamp,defines.NOT_PROC,size))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_get_change_for_path(self,watch_id,path,batch_size=1000):
        """
        Checks for an event for path greater or equal than watch_id (inclusive)
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select count(*) from FILE_CHANGES where id>? and path=?', (watch_id,path,)).fetchone()
        DB.dbcontroller.releaseConn()
        return res

    def watchdog_get_changes(self,watch_id,batch_size=1000):
        """
        Gets all the watchdog notification greater or equal than watch_id (inclusive), using the watch_id zero (0) will retrieve all changes
        The result is an iterator over the retrieved rows.
        The optional nbChanges specifies the size of the batch of rows to retrieve.
        """
        conn = DB.dbcontroller.getConn()
        res = conn.execute('select * from FILE_CHANGES where id>=?', (watch_id,)).fetchall()
        DB.dbcontroller.releaseConn()
        return res
        #return self.lazy_generator(my_cursor.fetchmany,batch_size)

    def watchdog_event_completed(self,watch_id):
        """
        Updates the process status of the watchdog table entry
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('update FILE_CHANGES set processed=? where id=?', (defines.PROC,watch_id,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_event_repeat(self,watch_id,size,timestamp):
        conn = DB.dbcontroller.getConn()
        conn.execute('update FILE_CHANGES set size=?,timestamp=? where id=?', (size,timestamp,watch_id,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_cleanup(self):
        """
        Deletes all the watchdog notifications marked as completed.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from FILE_CHANGES where processed=?', (defines.PROC,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def watchdog_cleanup_all(self):
        """
        Deletes all the watchdog notifications.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from FILE_CHANGES')
        conn.commit()
        DB.dbcontroller.releaseConn()


    def set_provider_token(self,provider,token,refresh=None,timestamp=None,token_expiry=None):
        """
        Stores the token for a given provider.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('insert or replace into PROVIDER_TOKENS values(?,?,?,?)', (provider,token,refresh,token_expiry))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def delete_provider_token(self,provider):
        """
        removes the token for a given provider.
        """
        conn = DB.dbcontroller.getConn()
        conn.execute('delete from PROVIDER_TOKENS where id=?', (provider,))
        conn.commit()
        DB.dbcontroller.releaseConn()

    def get_provider_token(self,provider):
        """
        Returns the token for the given provider, otherwise None.
        """
        conn = DB.dbcontroller.getConn()
        data = conn.execute('select * from PROVIDER_TOKENS where id=?', (provider,)).fetchone()
        DB.dbcontroller.releaseConn()
        if data != None:
            return data[1]

    def get_provider_refresh_token(self,provider):
        """
        Returns the refresh token for the given provider, otherwise None.
        """
        conn = DB.dbcontroller.getConn()
        data = conn.execute('select * from PROVIDER_TOKENS where id=?', (provider,)).fetchone()
        DB.dbcontroller.releaseConn()
        if data != None:
            return data[2]

    def get_provider_token_expiry(self,provider):
        """
        Returns the token expiry for the given provider, otherwise None.
        """
        conn = DB.dbcontroller.getConn()
        data = conn.execute('select * from PROVIDER_TOKENS where id=?', (provider,)).fetchone()
        DB.dbcontroller.releaseConn()
        if data != None:
            return data[3]

    def lazy_generator(self,fetch,batch_size):
        #FIXME: check how this works when concurrently inserting into the tables
        while True:
                rows = fetch(batch_size)
                if not rows: break
                for row in rows:
                    yield row


def simple_test():
       #TODO: convert to unit test
       print 'simple_test'
       db = DB()

       db.set_machine_id(1)
       db.set_machine_id(2)
       db.set_machine_id(3)
       print 'machine_id: ', db.get_machine_id()

       db.set_data_folder('/a/b/c/d')
       print 'data_folder: ', db.get_data_folder()

       db.set_local_provider_folder('/x/y/z')
       print 'local_provider: ', db.get_local_provider_folder()

       db.set_providers_list("123:456:789")
       print 'provider_list: ', db.get_providers_list()

       for x in range(20):
        db.add_block_to_file('/tmp/a.txt', x,  hashlib.sha1(str(x)).hexdigest())
       for x in range(5):
        db.add_block_to_file('/tmp/b.txt', x,  hashlib.sha1(str(x)).hexdigest())

       print 'getting all blocks from all files'
       for row in db.get_all_blocks_from_all_files():
        print row


       db.remove_block_from_file('/tmp/a.txt',11)
       print 'getting all blocks from all files after delete'
       for row in db.get_all_blocks_from_all_files():
        print row

       for x in range(3,5):
        db.add_block_to_file('/tmp/a.txt', x,  hashlib.sha1(str(x**2)).hexdigest())

       print 'getting all blocks from all files after update'
       for row in db.get_all_blocks_from_all_files():
        print row

       print 'getting blocks from file'
       for row in db.get_all_blocks_from_file('/tmp/a.txt'):
        print row

       print 'getting blocks from file at offset'
       print db.get_block_from_file('/tmp/a.txt',5)

       db.set_provider_token('dropbox','123456', datetime.datetime(2120,2,25) )
       print 'valid token: ', db.get_provider_token('dropbox')

       db.set_provider_token('skydrive','asdfgh', datetime.datetime(1920,2,25) )
       print 'expired token: ', db.get_provider_token('skydrive')

       db.set_provider_token('skydrive','asdfgh', datetime.datetime(2025,2,25) )
       print 'expired token: ', db.get_provider_token('skydrive')

       db.set_provider_token('skydrive','xyz', datetime.datetime(2025,2,25) )
       print 'renewed token: ', db.get_provider_token('skydrive')

       print 'inserting'
       db.add_path('/a/b/c/a.txt',defines.ADD,datetime.datetime.now() )
       db.add_path('/a/b/c/b.txt',defines.ADD,datetime.datetime.now() )
       db.add_path('/a/b/c/c.txt',defines.ADD,datetime.datetime.now() )
       db.add_path('/a/b/c/d.txt',defines.ADD,datetime.datetime.now() )
       print 'getting existing path: ', db.get_path('/a/b/c/d.txt')
       print 'getting non existing path: ', db.get_path('/a/b/c/d.txtASd')

       print 'getting all paths'
       for row in db.get_all_paths():
        print row

       print 'deleting non existing path: ',  db.remove_path('/a/b/c/d.txtaaa')
       print 'getting path: ', db.get_path('/a/b/c/d.txt')
       print 'deleting existing path: ',  db.remove_path('/a/b/c/d.txt')
       print 'getting deleted path: ', db.get_path('/a/b/c/d.txt')

       db.watchdog_path_created('/a/watchdog.txt', defines.FILE_TYPE)
       db.watchdog_path_created('/a/watchdog/', defines.FOLDER_TYPE)
       db.watchdog_path_modified('/a/watchdog/', defines.FOLDER_TYPE)
       db.watchdog_path_moved('/a/watchdog/', defines.FOLDER_TYPE, '/a/moved/')
       db.watchdog_path_deleted('/a/watchdog.txt', defines.FILE_TYPE)

       print 'getting all watchdog changes'
       data = db.watchdog_get_changes(0)
       for row in data:
        print row


       print 'getting some watchdog changes'
       data = db.watchdog_get_changes(3)
       for row in data:
        print row

       print 'deleting some watchdog changes'
       db.watchdog_cleanup(3)
       data = db.watchdog_get_changes(0)
       for row in data:
        print row


       print 'simple_test DONE'

if __name__ == "__main__":
    simple_test()
