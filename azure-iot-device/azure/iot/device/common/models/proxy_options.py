# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""
TODO
"""


class ProxyOptions(object):
    """
    TODO
    """

    def __init__(self, proxy_type, proxy_addr, proxy_username, proxy_password):
        self._proxy_type = proxy_type
        self._proxy_addr = proxy_addr
        self._proxy_username = proxy_username
        self._proxy_password = proxy_password

    @property
    def proxy_type(self):
        return self._proxy_type

    @property
    def proxy_address(self):
        return self._proxy_addr

    @property
    def proxy_username(self):
        return self._proxy_username

    @property
    def proxy_password(self):
        return self._proxy_password
