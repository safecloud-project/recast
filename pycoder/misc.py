import random
import string
from safestore.aes_driver import AESDriver


aes_driver = AESDriver()

#shamir = ShamirDriver(3, 2)
#xor = XorDriver(3)

msg = """
        0,203.508
        1,281.419
        2,322.512
        3,336.498
        4,342.959
        5,348.415
      """



def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

print(len(aes_driver.encode(msg)))

#message = randomword(110)
# print message
#sh = shamir.encode(message)

# print(xor.encode(message))
# print(sh)
# print(shamir.decode(sh))
