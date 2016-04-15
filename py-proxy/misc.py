from safestore.providers.one import ODrive
from safestore.providers.gdrive import GDrive
from safestore.providers.dbox import DBox

drive = DBox()
# onedrive 204.79.197.213
# gdrive www.googleapis.com
# dropbox content.dropboxapi.com

drive.put("ola", "cenas.txt")
print(drive.get("cenas.txt"))
drive.clean("/")