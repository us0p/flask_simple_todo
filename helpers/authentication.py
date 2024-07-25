import functools
from typing import Any, Callable

from flask import request

class AuthenticationHelper:
    @staticmethod
    def validate_token(fn: Callable[..., Any]):
        # preserves the decorated function metadata throghout the stack.
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return ({"error": "missing authorization token"}, 401)
            return fn(*args, **kwargs)
        return wrapper
