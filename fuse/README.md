# fuse
A python module to mount playcloud as a FUSE filesystem.

## Requirements
### System

* fuse

### Python
The requirements are listed in the requirements.txt file.

## Usage
To function, this module requires an instance of playcloud running on the same host (and reachable on 127.0.0.1:3000).
Once you have an instance of playcloud running, choose or create a mount point by and start the module.
```bash
python mount.py /mount/point
```

## Operations supported
In addition to operations to read files (cat or whatever dedicated program), the module currently supports the following unix commands:

* ls
* stat
* touch
* cp

## Run in a container
To run the code in a container, run the following commands.
```bash
# Build an image based on Dockerfile named fuse
docker build -t fuse .
# Start the container
docker run -it --rm --network=playcloud_default --hostname "fuse" --name fuse \
    --cap-add SYS_ADMIN --device /dev/fuse --security-opt apparmor:unconfined fuse
# Inside the container, run mount.py
/usr/local/src/fuse/mount.py --mountpoint /tmp/fuse
```
