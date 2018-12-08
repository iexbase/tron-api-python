# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------


class TronError(Exception):
    """Base class for TronAPI exceptions."""


class InvalidTronError(TronError):
    """Raised Tron Error"""


class FallbackNotFound(Exception):
    """
    Raised when fallback function doesn't exist in contract.
    """
    pass


class MismatchedABI(Exception):
    """
    Raised when an ABI does not match with supplied parameters, or when an
    attempt is made to access a function/event that does not exist in the ABI.
    """
    pass


class InvalidAddress(ValueError):
    """
    The supplied address does not have a valid checksum, as defined in EIP-55
    """
    pass


class NoABIFunctionsFound(AttributeError):
    """
    Raised when an ABI doesn't contain any functions.
    """
    pass


class ValidationError(Exception):
    """
    Raised when a supplied value is invalid.
    """
    pass


class TransportError(TronError):
    """Base exception for transport related errors.

    This is mainly for cases where the status code denotes an HTTP error, and
    for cases in which there was a connection error.

    """

    @property
    def status_code(self):
        return self.args[0]

    @property
    def error(self):
        return self.args[1]

    @property
    def info(self):
        return self.args[2]

    @property
    def url(self):
        return self.args[3]


class HttpError(TransportError):
    """Exception for errors occurring when connecting, and/or making a request"""


class BadRequest(TransportError):
    """Exception for HTTP 400 errors."""


class NotFoundError(TransportError):
    """Exception for HTTP 404 errors."""


class ServiceUnavailable(TransportError):
    """Exception for HTTP 503 errors."""


class GatewayTimeout(TransportError):
    """Exception for HTTP 503 errors."""


class TimeExhausted(Exception):
    """
    Raised when a method has not retrieved the desired result within a specified timeout.
    """
    pass


HTTP_EXCEPTIONS = {
    400: BadRequest,
    404: NotFoundError,
    503: ServiceUnavailable,
    504: GatewayTimeout,
}
