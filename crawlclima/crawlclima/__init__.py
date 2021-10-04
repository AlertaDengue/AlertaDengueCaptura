from importlib.metadata import PackageNotFoundError, version

__author__ = 'fccoelho'

try:
    __version__ = version('crawlclima')
except PackageNotFoundError:
    try:
        from ._version import __version__
    except Exception:
        __version__ = '0.0.0'
