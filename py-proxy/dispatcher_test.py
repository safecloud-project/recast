from safestore.providers.dispatcher import *
import os
import random
import string

config = {
	"entanglement": True,
	"providers": [
        {"type": "redis", "host": "localhost", "port": 7000},
        {"type": "redis", "host": "localhost", "port": 7001},
        {"type": "redis", "host": "localhost", "port": 7002}
	]
}


blocks = []

def randomword(length):
    return ''.join(random.choice(string.lowercase) for i in range(length))

for i in range(0, 3):
  blocks.append(randomword(4))

dispatcher = Dispatcher(config)
dispatcher.put("teste", blocks)
dispatcher.put("teste2", blocks)

rec_blocks = dispatcher.get("teste2")

print rec_blocks
#print dispatcher.disentangle(original_blocks, entangled_blocks)


