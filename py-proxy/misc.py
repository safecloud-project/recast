from safestore.providers.one import ODrive


drive = ODrive()

drive.put("ola", "cenas.txt")
print(drive.get("cenas.txt"))
drive.clean("/")