"""
An S3 backend for playcloud
"""
import os

import boto3

#TODO Implement an in-memory io.RawIOBase class that wraps the byte sequence as if it were file on disk


class S3Provider(object):
    """
    A playcloud backend that talks with an S3-compatible backend
    """
    def __init__(self,
                 bucket="playcloud",
                 endpoint_url="http://durable:9000",
                 aws_access_key_id="playcloud",
                 aws_secret_access_key="playcloud",
                 type="s3"):
        self.client = boto3.client("s3",
                                   endpoint_url=endpoint_url,
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

        self.bucket = bucket
        available_buckets = self.client.list_buckets()["Buckets"]
        for a_bucket in available_buckets:
            if a_bucket["Name"] == self.bucket:
                return
        self.client.create_bucket(Bucket=self.bucket)

    def get(self, path):
        """
        Args:
            path(str): Path to the block
        Returns:
            bytes: The data to return
        """
        temp_filename = "/tmp/{:s}-{:s}".format(self.bucket, path)
        self.client.download_file(self.bucket, path, temp_filename)
        with open(temp_filename, "rb") as handle:
            data = handle.read()
        os.remove(temp_filename)
        return data

    def put(self, data, path):
        """
        Args:
            data(bytes): Byte sequence of the file to store
            path(str): Key under which the data should be placed
        Returns:
            bool: True if the insertion worked
        """
        temp_filename = "/tmp/{:s}-{:s}".format(self.bucket, path)
        with open(temp_filename, "wb") as handle:
            handle.write(data)
        self.client.upload_file(temp_filename, self.bucket, path)
        os.remove(temp_filename)
        return os.path.isfile(temp_filename)

    def delete(self, path):
        """
        Args:
            path(str): Path to the file
        Returns:
            bool: True if the deletion succeeded
        """
        response = self.client.delete_object(Bucket=self.bucket, Key=path)
        return response["DeleteMarker"]
