"""MOISSCode Engine versioning."""

MAJOR = 3
MINOR = 0
PATCH = 2
LABEL = ""

__version__ = f"{MAJOR}.{MINOR}.{PATCH}" if not LABEL else f"{MAJOR}.{MINOR}.{PATCH}-{LABEL}"


def get_version():
    return __version__
