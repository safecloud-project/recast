#! /usr/bin/env python
# coding=utf8

import logging
import time
import os

from concurrent import futures

import pyproxy.safestore.handler.defines as defines



class Magic():

    def __init__(self, providers):
        self.providers = providers
        self.executor = futures.ThreadPoolExecutor(max_workers=len(providers))
        self.downloadBytes = 0
        self.uploadBytes = 0
        self.logger = logging.getLogger()
        self.logger.debug("Magic initialized.")

    def createDir(self, path):
        # Must go to all providers
        while True:
            try:
                res = []
                for i in range(0, len(self.providers)):
                    res.append(self.executor.submit(
                        self.providers[i].createDir, path))
                    self.logger.info("magic:createDir:i:" +
                                     str(i) + ":path:" + str(path))
                for i in range(0, len(res)):
                    res[i].result()
            except Exception as e:
                self.logger.error("Magic Exception: " + str(e))
                defines.retry_provider_op()
                continue
            defines.provider_op_resumed()
            break

    def put(self, data, path, prefix_dir=defines.BLOCKS_DIR):
        path = prefix_dir + path
        while True:
            try:
                list_cypher_data = cypher(data, len(self.providers))
                res = []
                for i in range(0, len(self.providers)):
                    res.append(self.executor.submit(self.providers[i].put, list_cypher_data[i], path))
                    self.logger.info("magic:put:i:" +
                                     str(i) + ":path:" + str(path))

                for i in range(0, len(res)):
                    res[i].result()
            except Exception as e:
                self.logger.error("Magic Exception: " + str(e))
                defines.retry_provider_op()
                continue
            defines.provider_op_resumed()
            break
        self.uploadBytes += len(data)

    def get(self, path, prefix_dir=defines.BLOCKS_DIR):
        path = prefix_dir + path
        while True:
            try:
                retry = True
                cont = 0
                while retry and cont < 5:
                    list_cypher_data = []
                    for provider in self.providers:
                        list_cypher_data.append(
                            self.executor.submit(provider.get, path))

                    if any(x.result() is None for x in list_cypher_data):
                        return None

                    retry = len(set([len(x.result())
                                     for x in list_cypher_data])) != 1

                    if retry:
                        time.sleep(1)
                        cont += 1
            except Exception:
                self.logger.exception("Magic Exception")
                defines.retry_provider_op()
                continue
            defines.provider_op_resumed()
            break

        raw_data_list = []
        for el in list_cypher_data:
            raw_data_list.append(el.result())

        data = decypher(raw_data_list)
        self.downloadBytes += len(data)
        return data

    def listChildren(self, path):
        return self.providers[0].listChildren(path)

    def delete(self, path, prefix_dir=defines.BLOCKS_DIR):
        path = prefix_dir + path
        while True:
            try:
                res = []
                for provider in self.providers:
                    res.append(self.executor.submit(provider.delete, path))
                for i in range(0, len(res)):
                    res[i].result()
            except Exception as e:
                self.logger.error("Magic Exception: " + str(e))
                defines.retry_provider_op()
                continue
            defines.provider_op_resumed()
            break

    def clean(self):
        while True:
            try:
                res = []
                for provider in self.providers:
                    res.append(self.executor.submit(
                        provider.clean, defines.SAFECLOUD_DIR))
                for i in range(0, len(res)):
                    res[i].result()
            except Exception as e:
                self.logger.error("Magic Exception: " + str(e))
                defines.retry_provider_op()
                continue
            defines.provider_op_resumed()
            break

    def quota(self):
        """Returns the current free space in bytes in the Drive
        """
        res = []
        for provider in self.providers:
            res.append(self.executor.submit(provider.quota))
        mins = []
        for i in range(0, len(res)):
            mins.append(res[i].result())
        return min(mins)

    def getUploadBytes(self):
        res = self.uploadBytes
        self.uploadBytes = 0
        return res

    def getDownloadBytes(self):
        res = self.downloadBytes
        self.downloadBytes = 0
        return res

    # nofutures
    '''
    def decypher(self,data):
        buf = data[0]
        self.logger.error(str(len(data)))
        for i in range(1, len(data)):
            self.logger.info("magic:decypher:"+str(i))
            self.logger.info("magic:decypher:"+str(len(buf)))
            self.logger.info("magic:decypher:"+str(data[i]))
            self.logger.info("magic:decypher:"+str(len(data[i])))
            buf=faster_xor(buf,data[i])
        return buf
    '''





def cypher(data, nr_providers):
    res = []
    buf = data
    size = len(data)
    for x in range(1, nr_providers):
        rnd = os.urandom(size)
        buf = faster_xor(buf, rnd)
        res.append(rnd)
    res.append(buf)
    return res



def decypher(data):
    buf = data[0]
    for i in range(1, len(data)):
        buf = faster_xor(buf, data[i])
    return buf
