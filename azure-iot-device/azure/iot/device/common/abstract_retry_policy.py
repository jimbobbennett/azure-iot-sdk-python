# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains abstract classes for Azure IoT SDK retry policies
"""

import six
import abc


@six.add_metaclass(abc.ABCMeta)
class AbstractRetryPolicy(object):
    @abc.abstractmethod
    def get_next_retry_interval(self, retry_count):
        """
        Computes the interval to wait before retrying an operation.

        @param {number} retry_count   Count of retries so far, including this one.  Set to 1 for the first retry.
        @returns {number}             The time to wait before attempting a retry in milliseconds.
        """
        pass

    @abc.abstractmethod
    def should_retry(self, error, retry_count):
        """
        Based on the error passed as argument, determines if an error is transient and if the operation should be retried or not.

        @param {Error} error            The error encountered by the operation.
        @param {number} retry_count     Count of retries so far, including this one.  Set to 1 for the first retry.
        @returns {boolean}              Whether the operation should be retried or not.
        """
        pass
