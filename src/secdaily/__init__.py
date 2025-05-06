"""
main __init__.py

Defines the version attribut of the library
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("secdaily")
except PackageNotFoundError:
    __version__ = "0.0.0"  # fallback if package not installed correctly
