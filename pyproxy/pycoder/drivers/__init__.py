import os

DRIVERS_MODULE_DIRECTORY = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
DRIVER_FILES = [os.path.join(DRIVERS_MODULE_DIRECTORY, f) for f in os.listdir(DRIVERS_MODULE_DIRECTORY)]
MODULES = [f for f in DRIVER_FILES if os.path.isfile(f) and f.endswith("_driver.py") and not "test" in f and not f.endswith("__init__.py")]
TRIMMED_MODULES = [f.replace(".py", "").replace("/", ".") for f in MODULES]
__all__ = map(__import__, TRIMMED_MODULES)
