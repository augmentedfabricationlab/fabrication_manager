

__all__ = [
    "nullcontext"
]


class nullcontext():
    def __enter__(cls):
        pass
    def __exit__(cls, typ, val, tb):
        pass