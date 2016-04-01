from providers.gdrive import GDrive


drive = GDrive()

drive.put("ola", "cenas.txt")
print(drive.get("cenas.txt"))