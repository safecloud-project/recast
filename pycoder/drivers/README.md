# Drivers
This folder contains custom drivers that can be used by pycoder to do erasure coding.

## Add a new driver
Adding a new driver can be done in a few simple steps:

 * Pick a name for your driver (eg: salty chocolate)
 * Create a file in this folder named by concatenating the words in the name of your drive in lower case and appending the suffix *\_driver.py* (eg: saltychocolate\_driver.py)
 * In the file add a class by translating the name of your class in camel case (eg: SaltychocolateDriver)

## Loading the driver
To load the driver, set the environment variable ec\_type to the filename containing your driver minus the *\_driver.py* suffix.
For instance to load the SaltychocolateDriver located in drivers/saltychocolate\_driver.py, set the ec\_type environment varianle to saltychocolate. 
