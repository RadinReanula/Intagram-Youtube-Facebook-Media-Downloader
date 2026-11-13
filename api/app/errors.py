from __future__ import annotations


class ApiError(Exception):
    def __init__(self, code: str, message: str, status: int = 400, **extra: object) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status
        self.extra = extra


def invalid_link(message: str = "That doesn't look like a valid link.") -> ApiError:
    return ApiError("invalid_link", message, 400)


def unsupported(message: str) -> ApiError:
    return ApiError("unsupported", message, 400)


def private_content(message: str = "This content is private or needs a login, so it can't be downloaded.") -> ApiError:
    return ApiError("private_content", message, 403)


def not_found(message: str = "This content was not found. It may have been deleted.") -> ApiError:
    return ApiError("not_found", message, 404)


def blocked(message: str = "The platform blocked the request. Try again later.") -> ApiError:
    return ApiError("blocked", message, 502)


def busy(message: str, **extra: object) -> ApiError:
    return ApiError("busy", message, 503, **extra)


def limit_exceeded(message: str) -> ApiError:
    return ApiError("limit_exceeded", message, 400)
