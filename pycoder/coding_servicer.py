"""Wrapper for pyeclib encoders using GRPC"""
from ConfigParser import ConfigParser
import os
import logging
import logging.config

from pyeclib.ec_iface import ECDriver

from custom_drivers import ECStripingDriver
from custom_drivers import PylonghairDriver
from playcloud_pb2 import BetaEncoderDecoderServicer
from playcloud_pb2 import DecodeReply
from playcloud_pb2 import EncodeReply
from playcloud_pb2 import Strip

from safestore.xor_driver import XorDriver
from safestore.hashed_splitter_driver import HashedSplitterDriver, IntegrityException
from safestore.signed_splitter_driver import SignedSplitterDriver
from safestore.signed_hashed_splitter_driver import SignedHashedSplitterDriver
from safestore.aes_driver import AESDriver
from safestore.shamir_driver import ShamirDriver
from safestore.assymetric_driver import AssymetricDriver

CONFIG = ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), "pycoder.cfg"))

log_config = os.getenv("LOG_CONFIG", "/usr/local/src/app/logging.conf")
logging.config.fileConfig(log_config)

logger = logging.getLogger("pycoder")


class DriverFactory():

    def __init__(self, config):

        #ignoring config for now
        self.config = config

        self.splitter = os.environ.get("splitter")
        self.sec_measure = os.environ.get("sec_measure")

    def setup_driver(self):

        splitters = {'xor': self.xor,
                     'shamir': self.shamir,
                     'ec': self.erasure_driver,
                     'aes': self.aes_driver
                     }

        self.splitter_driver = splitters[self.splitter]()

        measures = {  # just confidentiality
            'confd': self.confd,
            # confidentiality and integrity
            'confd_int': self.confd_int,
            # confidentiality and non-repudiation
            'confd_sign': self.confd_sign,
            # every guarantee
            'confd_int_sign': self.confd_int_sign}

        return measures[self.sec_measure]()

    def confd(self):
        return self.splitter_driver

    def confd_int(self):
        hash = os.environ.get("hash")
        driver = HashedSplitterDriver(self.splitter_driver, hash)
        return driver

    def _get_signer(self):
        sign_cypher = os.environ.get("signature")
        hash = os.environ.get("hash")
        key_size = int(os.environ.get("keysize"))
        return AssymetricDriver(sign_cypher, key_size, hash)

    def confd_sign(self):
        signer = self._get_signer()
        return SignedSplitterDriver(self.splitter_driver, signer)

    def confd_int_sign(self):
        signer = self._get_signer()
        return SignedHashedSplitterDriver(self.confd_int(), signer)

    def xor(self):
        nblocks = int(os.environ.get("n_blocks"))
        logger.info("{} nblocks".format(nblocks))
        return XorDriver(nblocks)

    def shamir(self):
        nblocks = int(os.environ.get("n_blocks"))
        threshold = int(os.environ.get("threshold"))

        logger.info("{} nblocks and {} threshold".format(nblocks, threshold))

        return ShamirDriver(nblocks, threshold)

    def erasure_driver(self):
        ec_k = int(os.environ.get("k"))
        ec_m = int(os.environ.get("m"))
        ec_type = os.environ.get("type")
        logger.info("ec_k {}, ec_m {}, ec_type {}".format(ec_k, ec_m, ec_type))
        return Eraser(ec_k, ec_m, ec_type)

    def aes_driver(self):
        return AESDriver()

    def get_driver(self):
        return self.setup_driver()





class Eraser(object):

    """A wrapper for pyeclib erasure coding driver (ECDriver)"""

    def __init__(self, ec_k, ec_m, ec_type="liberasurecode_rs_vand"):
        self.ec_type = ec_type
        self.aes = AESDriver()
        if ec_type == "pylonghair":
            self.driver = PylonghairDriver(k=ec_k, m=ec_m, ec_type=ec_type)
        elif ec_type == "striping" or ec_type == "bypass":
            self.driver = ECStripingDriver(k=ec_k, m=0, hd=None)
        else:
            self.driver = ECDriver(k=ec_k, m=ec_m, ec_type='jerasure_rs_vand')

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        enc = self.aes.encode(data)
        strips = self.driver.encode(enc[0])
        return strips

    def decode(self, strips):
        """Decode byte strips in a string of bytes"""
        data = self.driver.decode(strips)
        return self.aes.decode([data])


class HashedDriver():

    """
    Encapsulating driver for encryption schemes with hash.
    Converts the [(block, digest)] in to a list of [block, digest]
    when encoding.
    When decoding it converts the other way around.
    """


class Eraser(object):
    """A wrapper for pyeclib erasure coding driver (ECDriver)"""

    def __init__(self, k=8, m=2, ec_type="liberasurecode_rs_vand"):
        self.k=k
        self.m=m
        self.ec_type=ec_type
        if EC_TYPE == "pylonghair":
            self.driver=PylonghairDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)
        elif EC_TYPE == "striping" or EC_TYPE == "bypass":
            self.driver=ECStripingDriver(k=EC_K, m=0, hd=None)
        else:
            self.driver=ECDriver(k=EC_K, m=EC_M, ec_type=EC_TYPE)

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        strips=self.driver.encode(data)
        return strips_to_bytes(strips)

    def decode(self, data):
        """Decode a flattened string of byte strips in a string of bytes"""
        strips=bytes_to_strips(self.k, self.m, data)
        return self.driver.decode(strips)


class CodingService(BetaEncoderDecoderServicer):

    """
    An Encoder/Decoder built on top of playcloud.proto that can be loaded by a
    GRPC server
    """

    def Encode(self, request, context):
        """Encode data sent in an EncodeRequest into a EncodeReply"""
        reply = EncodeReply()
        logger.info("Received encode request")

        raw_strips = self.driver.encode(request.payload)

        log_temp = "Encoded and returned {} raw_strips"
        logger.debug(log_temp.format(len(raw_strips)))

        strips = []
        for raw_strip in raw_strips:
            strip = Strip()
            strip.data = raw_strip
            strips.append(strip)

        reply.strips.extend(strips)
        reply.parameters["splitter"] = os.environ.get("splitter", CONFIG.get("main", "splitter"))
        log_temp = "Request encoded, returning reply with {} strips"
        logger.info(log_temp.format(len(strips)))
        return reply

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        logger.info("Received decode request")

        reply = DecodeReply()
        strips = convert_strips_to_bytes_list(request.strips)
        reply.dec_block = self.driver.decode(strips)
        reply.parameters["splitter"] = os.environ.get("splitter", CONFIG.get("main", "splitter"))
        logger.info("Request decoded, returning reply")
        return reply
