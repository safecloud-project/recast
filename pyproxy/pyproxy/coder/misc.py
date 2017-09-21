import random
import string

from pyproxy.coder.safestore.shamir_driver import ShamirDriver


driver = ShamirDriver(5, 2)

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


encoded = driver.encode(msg)
encoded = map(lambda (x, y): str(x)+"<>"+y, encoded)
print(encoded)
rec_encoded = map(lambda x: (int(x.split('<>')[0]),x.split('<>')[1]), encoded)
print (rec_encoded)
print(driver.decode(rec_encoded))

#message = randomword(110)
# print message
#sh = shamir.encode(message)

# print(xor.encode(message))
# print(sh)
# print(shamir.decode(sh))
