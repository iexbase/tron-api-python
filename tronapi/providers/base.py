# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------

from tronapi.utils.help import format_user_agent


class BaseProvider(object):
    _status_page = None

    @property
    def status_page(self):
        """Get the page to check the connection"""
        return self._status_page

    @status_page.setter
    def status_page(self, page):
        self._status_page = page

    @staticmethod
    def _http_default_headers():
        """Add default headers"""
        return {
            'Content-Type': 'application/json',
            'User-Agent': format_user_agent()
        }
