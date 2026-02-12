"""MOISSCode Engine versioning."""

MAJOR = 1
MINOR = 1
PATCH = 0
LABEL = ""

__version__ = f"{MAJOR}.{MINOR}.{PATCH}" if not LABEL else f"{MAJOR}.{MINOR}.{PATCH}-{LABEL}"


def get_version():
    return __version__
