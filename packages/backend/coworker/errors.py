"""Errors whose messages are written for the person using the app.

Endpoints must not echo arbitrary exception text to clients: a library or
provider exception can carry internals (paths, queries, stack details).
Raise a ``UserFacingError`` subclass when the message is meant for the
user; ``public_message()`` returns that message and turns anything else
into a generic one (logging the real exception server-side).

The subclasses also inherit from the matching built-in, so existing
``except ValueError`` / ``PermissionError`` / ``RuntimeError`` handlers
keep catching them.
"""
from __future__ import annotations

import logging

log = logging.getLogger("coworker.errors")

GENERIC_MESSAGE = "Something went wrong. Please try again."


class UserFacingError(Exception):
    """Base for errors whose message is safe to show to the user."""

    def __init__(self, message: str = "", *args: object) -> None:
        super().__init__(message, *args)
        # Captured from the raise site's own text, never from another
        # exception, so it can't carry library internals.
        self.public_message = str(message)


class InvalidInput(UserFacingError, ValueError):
    """The request's input was rejected (shown to the user as-is)."""


class ConsentRequired(UserFacingError, PermissionError):
    """An action needs consent or verification the user hasn't given yet."""


class NotConfigured(UserFacingError, RuntimeError):
    """A feature needs server configuration that isn't present."""


def public_message(exc: BaseException, fallback: str = GENERIC_MESSAGE) -> str:
    """Message to show a client for ``exc``.

    App-defined errors return their own message; anything else is logged
    with its traceback and replaced by ``fallback``.
    """
    if isinstance(exc, UserFacingError) and exc.public_message:
        return exc.public_message
    log.error("Hiding internal error from the client", exc_info=exc)
    return fallback
