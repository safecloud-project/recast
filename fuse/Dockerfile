FROM ubuntu:latest

# Install fuse and python dependencies
RUN apt-get update && apt-get install fuse python python-numpy python-pip --assume-yes --quiet && \
    pip install --upgrade pip --quiet

# Copy sources
COPY mount.py /usr/local/src/fuse/
COPY benchmark.py /usr/local/src/fuse/
COPY requirements.txt /usr/local/src/fuse/
RUN chmod +x /usr/local/src/fuse/mount.py

# Install runtime dependencies
RUN pip install --requirement /usr/local/src/fuse/requirements.txt

# Set up default environment values
RUN mkdir --parents /tmp/fuse
ENV MOUNT_POINT /tmp/fuse
ENV HOST proxy
ENV PORT 8000

# Entrypoint
# ENTRYPOINT ["/usr/local/src/fuse/mount.py",  "--mountpoint", "${MOUNT_POINT}", "--host", "${HOST}", "--port", "${PORT}"]
