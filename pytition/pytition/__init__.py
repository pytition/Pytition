import os

_NO_VALUE = object()


def getenv_bool(name, default=_NO_VALUE):
    val = os.getenv(name)
    if val is None and default is _NO_VALUE:
        raise ValueError(
            f"{name} is not present in environment variables "
            "and no default value was provided"
        )

    val = str(val).lower().strip()
    truthy = ("y", "yes", "t", "true", "on", "1")
    falsy = ("n", "no", "f", "false", "off", "0")
    if val in truthy:
        return True
    elif val in falsy:
        return False
    elif default is not _NO_VALUE:
        return default
    else:
        raise ValueError(
            "Invalid boolean value %r, authorized values are %r and %r"
            % (val, truthy, falsy)
        )
