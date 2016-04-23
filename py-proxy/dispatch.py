from safestore.providers.dispatcher import Dispatcher, xor

DATA = ["hello", "world"]

dispatcher = Dispatcher({
    "entanglement": {
        "enabled": True,
        "p": 2
    },
    "providers": [
        {"type": "redis"}
    ]
})


dispatcher.put("one", DATA)
dispatcher.put("two", DATA)
dispatcher.put("three", DATA)
dispatcher.put("four", DATA)
dispatcher.put("five", DATA)
dispatcher.put("six", DATA)
dispatcher.put("seven", DATA)
dispatcher.put("eight", DATA)
dispatcher.put("nine", DATA)
dispatcher.put("ten", DATA)

print [x.key for x in dispatcher.files.get("one").entangling_blocks], "\t", dispatcher.get("one")
print [x.key for x in dispatcher.files.get("two").entangling_blocks], "\t", dispatcher.get("two")
print [x.key for x in dispatcher.files.get("three").entangling_blocks], "\t", dispatcher.get("three")
print [x.key for x in dispatcher.files.get("four").entangling_blocks], "\t", dispatcher.get("four")
print [x.key for x in dispatcher.files.get("five").entangling_blocks], "\t", dispatcher.get("five")
print [x.key for x in dispatcher.files.get("six").entangling_blocks], "\t", dispatcher.get("six")
print [x.key for x in dispatcher.files.get("seven").entangling_blocks], "\t", dispatcher.get("seven")
print [x.key for x in dispatcher.files.get("eight").entangling_blocks], "\t", dispatcher.get("eight")
print [x.key for x in dispatcher.files.get("nine").entangling_blocks], "\t", dispatcher.get("nine")
print [x.key for x in dispatcher.files.get("ten").entangling_blocks], "\t", dispatcher.get("ten")
