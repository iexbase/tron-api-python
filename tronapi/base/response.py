# --------------------------------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
from http import HTTPStatus
from tronapi.exceptions import TronRequestError


class TronResponse:
    """Encapsulates an http response from Tron."""

    def __init__(self, body=None, http_status=None, headers=None, call=None):
        """Initializes the object's internal data.
        Args:
            body (optional): The response body as text.
            http_status (optional): The http status code.
            headers (optional): The http headers.
            call (optional): The original call that was made.
        """
        self._body = body
        self._http_status = http_status
        self._headers = headers or {}
        self._call = call

        if self._http_status in (404, 502, 500):
            self._body = {
                'error': 'Request failed, try again'
            }

    def body(self):
        """Returns the response body."""
        return self._body

    def json(self):
        """Returns the response body -- in json if possible."""
        try:
            return json.loads(self._body)
        except (TypeError, ValueError):
            return self._body

    def headers(self):
        """Return the response headers."""
        return self._headers

    def etag(self):
        """Returns the ETag header value if it exists."""
        return self._headers.get('ETag')

    def status(self):
        """Returns the http status code of the response."""
        return self._http_status

    def is_success(self) -> bool:
        """Returns boolean indicating if the call was successful."""
        if self._http_status == HTTPStatus.NOT_MODIFIED.value:
            # ETAG Hit
            return True
        elif self._http_status == HTTPStatus.OK.value:
            # HTTP Okay
            return True
        else:
            # Something else
            return False

    def is_failure(self) -> bool:
        """Returns boolean indicating if the call failed."""
        return not self.is_success()

    def error(self):
        """
        Returns a TronRequestError (located in the exceptions module) with
        an appropriate debug message.
        """
        if self.is_failure():
            return TronRequestError(
                "Call was not successful",
                self._call,
                self.status(),
                self.headers(),
                self.body(),
            )
        else:
            return None
