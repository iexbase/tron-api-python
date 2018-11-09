# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import json
import re


class TronError(Exception):
    """Base class for TronAPI exceptions."""
    pass


class InvalidTronError(TronError):
    """Raised Tron Error"""
    pass


class TronRequestError(TronError):
    """
    Raised when an api request fails. Returned by error() method on a
    TronResponse object returned through a callback function (relevant
    only for failure callbacks) if not raised at the core api call method.
    """

    def __init__(
            self, message=None,
            request_context=None,
            http_status=None,
            http_headers=None,
            body=None
    ):
        """"Create a new :class:`~.TronRequestError` instance.

        Args:
            message (str, optional): Text message
            request_context(object, optional): Context
            http_status (int): Status code
            http_headers (object, optional): Headers
            body (object, optional): Contents

        """
        self.message = message
        self.request_context = request_context
        self.http_status = http_status
        self.http_headers = http_headers

        try:
            self._body = json.loads(body)
        except (TypeError, ValueError):
            self._body = body

        self._api_error_code = None
        self._api_error_type = None
        self._api_error_message = None

        if self._body and 'error' in self._body:
            self._error = self._body['error']
            if 'message' in self._error:
                self._api_error_message = self._error['message']
            if 'code' in self._error:
                self._api_error_code = self._error['code']
            if 'type' in self._error:
                self._api_error_type = self._error['type']
        else:
            self._error = None

        request = self.request_context
        super(TronRequestError, self).__init__(
            "\n\n" +
            "  Message: %s\n" % self.message +
            "  Method:  %s\n" % request.get('method') +
            "  Path:    %s\n" % request.get('path', '/') +
            "  Params:  %s\n" % request.get('params') +
            "\n" +
            "  Status:  %s\n" % self.http_status +
            "  Response:\n    %s" % re.sub(
                r"\n", "\n    ",
                json.dumps(self._body, indent=2)
            ) +
            "\n"
        )
