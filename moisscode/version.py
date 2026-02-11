"""MOISSCode Engine versioning."""

MAJOR = 1
MINOR = 0
PATCH = 0
LABEL = "beta"

__version__ = f"{MAJOR}.{MINOR}.{PATCH}-{LABEL}"


def get_version():
    return __version__
