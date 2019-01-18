# --------------------------------------------------------------------
# Copyright (c) iEXBase. All rights reserved.
# Licensed under the MIT License.
# See License.txt in the project root for license information.
# --------------------------------------------------------------------
import platform

import tronapi


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
            'User-Agent': BaseProvider.format_user_agent()
        }

    @staticmethod
    def format_user_agent(name=None):
        """Construct a User-Agent suitable for use in client code.
        This will identify use by the provided ``name`` (which should be on the
        format ``dist_name/version``), TronAPI version and Python version.
        .. versionadded:: 1.1
        """
        parts = ['TronAPI/%s' % tronapi.__version__,
                 '%s/%s' % (platform.python_implementation(),
                            platform.python_version())]
        if name:
            parts.insert(0, name)
        return ' '.join(parts)
