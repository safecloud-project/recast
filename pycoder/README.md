# pycoder
An encoder/decoder for the playcloud project.

## Requirements
pycoder is a python application built on top of PyECLib. The following tools and libraries are required to use it.

* Python 2.7
* PyECLib 1.0.8
* grpcio 0.11
* liberasure

A dockerfile to build a ready-to-run environment is provided. The image can be built by running this command at the root of the pycoder directory.

```bash
docker build -t pycoder .
```
## Configuration
The application can be configured by tuning the values in pycoder.cfg. This can be useful to change the encoding settings passed to the pyeclib driver.

Please note that the configuration is read at the application startup. Changes made to the configuration file at runtime require an application restart to be taken into account.

### GRPC section
The address and port that the application listens on can be configured here.

### EC section
The number of data disks(k), parity disks(m) and the type of erasure coding can be configured here.
Please refer to [PyECLib's documentation](https://pypi.python.org/pypi/PyECLib) for suitable values.


## Start the server
To launch the application, just run the command

```bash
python server.py
```

This command will start the grpc server listening on the port defined in pycoder.cfg under the grpc section (defaults to 1234).
