"""Wrapper for pyeclib encoders using GRPC"""
from ConfigParser import ConfigParser
import uuid
import os
import hashlib
import logging
import logging.config

from pyeclib.ec_iface import ECDriver
from pyeclib.ec_iface import ECBackendInstanceNotAvailable
from pyeclib.ec_iface import ECBackendNotSupported
from pyeclib.ec_iface import ECInvalidParameter
from pyeclib.ec_iface import ECOutOfMemory
from pyeclib.ec_iface import ECDriverError

from entangled_driver import StepEntangler

from playcloud_pb2 import BetaEncoderDecoderServicer
from playcloud_pb2 import DecodeReply
from playcloud_pb2 import EncodeReply
from playcloud_pb2 import ReconstructReply
from playcloud_pb2 import Strip

from proxy_client import ProxyClient

from safestore.xor_driver import XorDriver
from safestore.hashed_splitter_driver import HashedSplitterDriver
from safestore.signed_splitter_driver import SignedSplitterDriver
from safestore.signed_hashed_splitter_driver import SignedHashedSplitterDriver
from safestore.aes_driver import AESDriver
from safestore.shamir_driver import ShamirDriver
from safestore.assymetric_driver import AssymetricDriver


__LOCAL_DIRECTORY = os.path.dirname(__file__)

CONFIG = ConfigParser()
CONFIG.read(os.path.join(__LOCAL_DIRECTORY, "pycoder.cfg"))

log_config = os.getenv("LOG_CONFIG", os.path.join(__LOCAL_DIRECTORY, "logging.conf"))
logging.config.fileConfig(log_config)

logger = logging.getLogger("pycoder")


def should_be_deactivated(message):
    """
    Determines whether a message stands for an option to be turned off.
    Args:
        message(str): A message to test
    Returns:
        bool: True if the message is negative, False otherwise
    """
    NEGATIVE_TERMS = ["deactivated", "disabled", "false", "no", "none", "off"]
    return message.strip().lower() in NEGATIVE_TERMS

class DriverFactory(object):

    def __init__(self, config):

        #ignoring config for now
        self.config = config

        if os.environ.has_key("splitter"):
            self.splitter = os.environ.get("splitter")
        elif self.config.has_option("main", "splitter"):
            self.splitter = self.config.get("main", "splitter")
        else:
            raise RuntimeError("A value must be defined for the splitter to use either in pycoder.cfg or as an environment variable SPLITTER")

        if os.environ.has_key("sec_measure"):
            self.sec_measure = os.environ.get("sec_measure")
        elif self.config.has_option("main", "sec_measure"):
            self.sec_measure = self.config.get("main", "sec_measure")
        else:
            raise RuntimeError("A value must be defined for the security measure to use either in pycoder.cfg or as an environment variable SEC_MEASURE")
        self.splitter_driver = None


    def setup_driver(self):

        splitters = {
            "xor": self.xor,
            "shamir": self.shamir,
            "ec": self.erasure_driver,
            "aes": self.aes_driver,
            "entanglement": self.entanglement_driver
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
        hashing_scheme = os.environ.get("hash")
        driver = HashedSplitterDriver(self.splitter_driver, hashing_scheme)
        return driver

    def _get_signer(self):
        sign_cypher = os.environ.get("signature")
        hashing_scheme = os.environ.get("hash")
        key_size = int(os.environ.get("keysize"))
        return AssymetricDriver(sign_cypher, key_size, hashing_scheme)

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
        ec_k = None
        if os.environ.has_key("k"):
            ec_k = int(os.environ.get("k"))
        elif self.config.has_option("ec", "k"):
            ec_k = int(self.config.get("ec", "k"))
        else:
            raise RuntimeError("A value must be defined for the numer of data fragments (k) to use either in pycoder.cfg or as an environment variable K")

        ec_m = None
        if os.environ.has_key("m"):
            ec_m = int(os.environ.get("m"))
        elif self.config.has_option("ec", "m"):
            ec_m = int(self.config.get("ec", "m"))
        else:
            raise RuntimeError("A value must be defined for the number of parity fragments (m) to use either in pycoder.cfg or as an environment variable M")

        ec_type = None
        if os.environ.has_key("type"):
            ec_type = os.environ.get("type")
        elif self.config.has_option("ec", "type"):
            ec_type = self.config.get("ec", "type")
        else:
            raise RuntimeError("A value must be defined for the erasure coding type to use either in pycoder.cfg or as an environment variable TYPE")
        logger.info("ec_k %d, ec_m %d, ec_type %s", ec_k, ec_m, ec_type)
        # AES encryption is activated by default when using erasure coding
        # To deactivate it, set the aes env variable or aes in the main section of pycoder.cfg
        # to off
        aes_enabled = True
        if os.environ.has_key("aes") and should_be_deactivated(os.environ.get("aes")):
            aes_enabled = False
        elif self.config.has_option("main", "aes") and should_be_deactivated(self.config.get("main", "aes")):
            aes_enabled = False
        return Eraser(ec_k, ec_m, ec_type, aes_enabled=aes_enabled)

    def aes_driver(self):
        return AESDriver()

    def entanglement_driver(self):
        """
        Returns an entanglement_driver
        Returns:
            EntanglementDriver: An instance of EntanglementDriver
        """
        driver = StepEntangler(5, 5, 5)
        logger.info("Loaded entanglement driver " + str(driver))
        return driver


    def get_driver(self):
        return self.setup_driver()


def convert_strips_to_bytes_list(playcloud_strips):
    """Extract the data bytes from alist of playcloud strips"""
    return [strip.data for strip in playcloud_strips]


class Eraser(object):

    """A wrapper for pyeclib erasure coding driver (ECDriver)"""

    def __init__(self, ec_k, ec_m, ec_type="liberasurecode_rs_vand", aes_enabled=True):
        self.ec_type = ec_type
        if aes_enabled:
            self.aes = AESDriver()
            logger.info("Eraser will use AES encryption")
        else:
            logger.info("Eraser will not use AES encryption")
        expected_module_name = "drivers." + ec_type.lower() + "_driver"
        expected_class_name = ec_type[0].upper() + ec_type[1:].lower() + "Driver"
        try:
            mod = __import__(expected_module_name, fromlist=[expected_class_name])
            driver_class = None
            driver_class = getattr(mod, expected_class_name)
            self.driver = driver_class(k=ec_k, m=ec_m, ec_type=ec_type, hd=None)
        except (ImportError, AttributeError):
            logger.exception("Driver " + ec_type + " could not be loaded as a custom driver")
            try:
                self.driver = ECDriver(k=ec_k, m=ec_m, ec_type=ec_type)
            except Exception as error:
                logger.exception("Driver " + ec_type + " could not be loaded by pyeclib")
                raise error

    def encode(self, data):
        """Encode a string of bytes in flattened string of byte strips"""
        payload = data
        if hasattr(self, 'aes'):
            payload = self.aes.encode(data)[0]
        strips = self.driver.encode(payload)
        return strips

    def decode(self, strips):
        """Decode byte strips in a string of bytes"""
        payload = self.driver.decode(strips)
        if hasattr(self, 'aes'):
            return self.aes.decode([payload])
        return payload

    def reconstruct(self, available_payload_fragments, missing_indices):
        """
        Reconstruct missing fragments of data
        Args:
            available_payload_fragments(list(bytes)): Available fragments of data
            missing_indices(list(int)): List of the indices of the missing blocks
        Returns:
            list(bytes): A list of the reconstructed fragments
        """
        return self.driver.reconstruct(available_payload_fragments, missing_indices)

    def fragments_needed(self, missing_indices):
        """
        Return a list of the fragments needed to recover the missing ones
        Args:
            missing_indices(list(int)): The list of indices of the fragments to recover
        Returns:
            list(int): A list of the indices of the fragments required to recover the missing ones
        """
        return self.driver.fragments_needed(missing_indices)

class HashedDriver(object):

    """
    Encapsulating driver for encryption schemes with hash.
    Converts the [(block, digest)] in to a list of [block, digest]
    when encoding.
    When decoding it converts the other way around.
    """

    def __init__(self, driver):
        self.driver = driver

    def _flat(self, data):
        return [item for sublist in data for item in sublist]

    def encode(self, data):
        encoded_data = self.driver.encode(data)
        res = self._flat(map(lambda (x, y): [x, y], encoded_data))
        return res

    def decode(self, data):
        result = []
        for i in range(0, len(data), 2):
            result.append((data[i], data[i + 1]))
        return self.driver.decode(result)


class CodingService(BetaEncoderDecoderServicer):

    """
    An Encoder/Decoder built on top of playcloud.proto that can be loaded by a
    GRPC server
    """

    def __init__(self):
        factory = DriverFactory(CONFIG)
        self.driver = factory.get_driver()

    def Encode(self, request, context):
        """Encode data sent in an EncodeRequest into a EncodeReply"""
        try:
            reply = EncodeReply()
            logger.info("Received encode request for " + str(request.parameters["key"]))
            raw_strips = self.driver.encode(request.payload)
            log_temp = "Encoded and returned {} raw_strips"
            logger.debug(log_temp.format(len(raw_strips)))

            fragments_needed = self.driver.fragments_needed([])

            strips = []
            for index, raw_strip in enumerate(raw_strips):
                # Copy data
                strip = Strip()
                # Create random id
                strip.id = str(uuid.uuid4())
                strip.data = raw_strip
                # Compute checksum
                checksum = hashlib.sha256(raw_strip).digest()
                strip.checksum = checksum
                # Mark data type
                if index in fragments_needed:
                    strip.type = Strip.DATA
                else:
                    strip.type = Strip.PARITY
                # Add strip
                strips.append(strip)
            reply.file.strips.extend(strips)
            reply.file.original_size = len(request.payload)
            reply.parameters["splitter"] = os.environ.get("splitter", CONFIG.get("main", "splitter"))
            log_temp = "Request encoded, returning reply with {} strips"
            logger.info(log_temp.format(len(strips)))
            return reply
        except (ECBackendInstanceNotAvailable, ECBackendNotSupported, ECInvalidParameter, ECOutOfMemory, ECDriverError) as error:
            logger.exception("An exception was while caught encoding blocks")
            raise error

    def Decode(self, request, context):
        """Decode data sent in an DecodeRequest into a DecodeReply"""
        try:
            logger.info("Received decode request")

            reply = DecodeReply()
            strips = convert_strips_to_bytes_list(request.strips)
            reply.dec_block = self.driver.decode(strips)
            reply.parameters["splitter"] = os.environ.get("splitter", CONFIG.get("main", "splitter"))
            logger.info("Request decoded, returning reply")
            return reply
        except (ECBackendInstanceNotAvailable, ECBackendNotSupported, ECInvalidParameter, ECOutOfMemory, ECDriverError) as error:
            logger.exception("An exception was while caught decoding blocks")
            raise error

    def Reconstruct(self, request, context):
        """
        Reconstruct blocks.
        Args:
            request(ReconstructRequest): A playcloud GRPC request
            context():
        Returns:
            ReconstructReply: The reconstructed blocks
        """
        logger.info("Received reconstruct request")
        path = request.path
        missing_indices = [int(index) for index in request.missing_indices]
        logger.debug("Retrieved path " + path + " and missing indices (" + ",".join([str(i) for i in missing_indices]) + ")")
        fragments_needed = self.driver.fragments_needed(missing_indices)
        logger.debug("Retrieved the list of indices to retrieve (" + "".join([str(i) for i in fragments_needed]) + ")")
        client = ProxyClient()
        available_payload_fragments = []
        for index in fragments_needed:
            logger.debug("Fetching block " + path + "[" + str(index) + "]")
            data = client.get_block(path, index).data
            available_payload_fragments.append(data)
            logger.debug("Retrieved block " + path + "[" + str(index) + "]")
        logger.debug("Reconstructing missing fragments [" + ",".join([str(i) for i in missing_indices])  + "]")
        reconstructed_data = self.driver.reconstruct(available_payload_fragments, missing_indices)
        logger.debug("Reconstructed missing fragments [" + ",".join([str(i) for i in missing_indices])  + "]")
        reply = ReconstructReply()
        for i, missing_index in enumerate(missing_indices):
            reply.reconstructed[missing_index].data = reconstructed_data[i]
        logger.info("Replying reconstruct request")
        return reply
