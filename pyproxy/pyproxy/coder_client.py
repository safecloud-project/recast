"""
Client implementation and util functions to interact with EncoderDecoder service
"""
#TODO: Move encode and decode calls to the CoderClient class
import grpc


from pyproxy.playcloud_pb2 import DecodeRequest, EncodeRequest, File, FragmentsNeededRequest, ReconstructRequest, Strip
import pyproxy.coder.coding_servicer
import pyproxy.playcloud_pb2_grpc as playcloud_pb2_grpc

DEFAULT_GRPC_TIMEOUT_IN_SECONDS = 60

class CoderClient(object):
    """
    A GRPC client for the coder service
    """
    def __init__(self, host="coder", port=1234):
        server_listen = host + ":" + str(port)
        grpc_message_size = (2 * 1024 * 1024 * 1024) - 1 # 2^31 - 1
        grpc_options = [
            ("grpc.max_receive_message_length", grpc_message_size),
            ("grpc.max_send_message_length", grpc_message_size)
        ]
        grpc_channel = grpc.insecure_channel(server_listen, options=grpc_options)
        self.stub = playcloud_pb2_grpc.EncoderDecoderStub(grpc_channel)

    def encode(self, key, data):
        """
        Sends data to the encoder for decoding
        Args:
            key(str): Path of the file
            data(bytes): Data to encode
        Returns:
            list(File): The encoded file
        """
        encode_request = EncodeRequest()
        encode_request.payload = data
        encode_request.parameters["key"] = key
        encoded_file = self.stub.Encode(encode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).file
        return encoded_file

    def decode(self, key, strips):
        """
        Sends data to the encoder for decoding.
        Args:
            key(str): Path of the file
            list(Strip): Strips to decode
        Returns:
            bytes: Decoded data
        """
        decode_request = DecodeRequest()
        decode_request.strips.extend(strips)
        decode_request.path = key
        decoded_file = self.stub.Decode(decode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).dec_block
        return decoded_file

    def reconstruct(self, path, missing_indices):
        """
        Returns reconstructed blocks.
        Args:
            path(str): Path to the file whose blocks need to be reconstructed
            missing_indices(list(int)): A list of the indices of the missing indices
        Returns:
            dict(int, Strip): A list of reconstructed blocks
        Raise:
            ValueError: if the path to the file is empty
        """
        if len(path.strip()) == 0:
            raise ValueError("path argument cannot be empty")
        if len(missing_indices) == 0:
            return []
        request = ReconstructRequest()
        request.path = path
        request.missing_indices.extend(missing_indices)
        reply = self.stub.Reconstruct(request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS)
        reconstructed = {}
        for index, value in reply.reconstructed.iteritems():
            reconstructed[int(index)] = value
        return reconstructed

    def fragments_needed(self, missing_indices):
        """
        Returns the block indices to compensate for the missing block indices
        Args:
            missing_indices(list(int)): Missing block indices
        Returns:
            list(int): List of the block indices to use when compensating for the missing ones
        Raises:
            ValueError: If he missing_indices argument is not of type list
        """
        if not isinstance(missing_indices, list):
            raise ValueError("missing_indices argument must be of type list")
        request = FragmentsNeededRequest()
        request.missing.extend(missing_indices)
        reply = self.stub.FragmentsNeeded(request)
        return [index for index in reply.needed]

class LocalCoderClient(object):
    def __init__(self):
        self.coding_service = pyproxy.coder.coding_servicer.CodingService()

    def encode(self, key, data):
        """
        Sends data to the encoder for decoding
        Args:
            key(str): Path of the file
            data(bytes): Data to encode
        Returns:
            list(File): The encoded file
        """
        encode_request = EncodeRequest()
        encode_request.payload = data
        encode_request.parameters["key"] = key
        encoded_file = self.coding_service.Encode(encode_request, None).file
        return encoded_file

    def decode(self, key, strips):
        """
        Sends data to the encoder for decoding.
        Args:
            key(str): Path of the file
            list(Strip): Strips to decode
        Returns:
            bytes: Decoded data
        """
        decode_request = DecodeRequest()
        decode_request.strips.extend(strips)
        decode_request.path = key
        decoded_file = self.coding_service.Decode(decode_request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS).dec_block
        return decoded_file

    def reconstruct(self, path, missing_indices):
        """
        Returns reconstructed blocks.
        Args:
            path(str): Path to the file whose blocks need to be reconstructed
            missing_indices(list(int)): A list of the indices of the missing indices
        Returns:
            dict(int, Strip): A list of reconstructed blocks
        Raise:
            ValueError: if the path to the file is empty
        """
        if len(path.strip()) == 0:
            raise ValueError("path argument cannot be empty")
        if len(missing_indices) == 0:
            return []
        request = ReconstructRequest()
        request.path = path
        request.missing_indices.extend(missing_indices)
        reply = self.coding_service.Reconstruct(request, DEFAULT_GRPC_TIMEOUT_IN_SECONDS)
        reconstructed = {}
        for index, value in reply.reconstructed.iteritems():
            reconstructed[int(index)] = value
        return reconstructed

    def fragments_needed(self, missing_indices):
        """
        Returns the block indices to compensate for the missing block indices
        Args:
            missing_indices(list(int)): Missing block indices
        Returns:
            list(int): List of the block indices to use when compensating for the missing ones
        Raises:
            ValueError: If he missing_indices argument is not of type list
        """
        if not isinstance(missing_indices, list):
            raise ValueError("missing_indices argument must be of type list")
        request = FragmentsNeededRequest()
        request.missing.extend(missing_indices)
        reply = self.coding_service.FragmentsNeeded(request)
        return [index for index in reply.needed]
