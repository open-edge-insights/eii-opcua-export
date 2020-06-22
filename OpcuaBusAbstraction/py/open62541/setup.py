"""
  setup file
"""
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# By default, -Wformat -Wformat-security compile flags
# are used, so not including it in extra_compile_flags
COMPILE_ARGS = ['-std=c99', '-g']
LINK_ARGS = ["-z", "noexecstack", "-z", "relro", "-z", "now"]
EXTENSION_NAME = "open62541W"
SOURCES = ["open62541W.pyx",
           "../../c/open62541/src/open62541_wrappers.c",
           "../../c/open62541/src/open62541.c",
           "../../c/DataBus.c"]
INCLUDE_DIRS = ["../../c/open62541/include",
                "../../c"]
LIBRARY_DIRS = ["."]
LIBRARIES = ["mbedtls", "mbedx509", "safestring",
             "mbedcrypto", "pthread"]

setup(
    name=EXTENSION_NAME,
    ext_modules=cythonize([Extension(EXTENSION_NAME,
                                     SOURCES,
                                     include_dirs=INCLUDE_DIRS,
                                     library_dirs=LIBRARY_DIRS,
                                     libraries=LIBRARIES,
                                     language="c",
                                     extra_compile_args=COMPILE_ARGS,
                                     extra_link_args=LINK_ARGS)]),
)
