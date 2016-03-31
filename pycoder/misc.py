import random
import string
from safestore.xor_driver import XorDriver
from safestore.shamir_driver import ShamirDriver


shamir = ShamirDriver(3, 2)
xor = XorDriver(3)


def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))


message = randomword(110)
print message
sh = shamir.encode(message)

#print(xor.encode(message))
print(sh)
print(shamir.decode(sh))