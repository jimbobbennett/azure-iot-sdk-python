# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains abstract classes for the various clients of the Azure IoT Hub Device SDK
"""

import logging
import random
from .abstract_retry_policy import AbstractRetryPolicy

logger = logging.getLogger(__name__)


class ExponentialBackoffWithJitter(AbstractRetryPolicy):
    """
     Implements an Exponential Backoff with Jitter retry strategy.
     The function to calculate the next interval is the following:

     F(x) = min(Cmin+ (2^(x-1)-1) * rand(C * (1–Jd), C * (1+Ju)), Cmax)

     Where:
     x = retry count (1 after first failure, 2 after second, etc)
     C = backoff interval
     Jd = jitter down percentage
     Ju = jitter up percentage
     Cmin = minimum retry interval
     Cmax = maximum retry interval
    """

    def __init__(
        self,
        retry_error_list,
        retry_op_list,
        immediate_first_retry,
        backoff_interval,
        minimum_interval_between_retries,
        maximum_interval_between_retries,
        jitter_up_factor,
        jitter_down_factor,
    ):
        self.retry_error_list = list(retry_error_list)
        self.retry_op_list = list(retry_op_list)
        self.immediate_first_retry = immediate_first_retry
        self.backoff_interval = backoff_interval
        self.minimum_interval_between_retries = minimum_interval_between_retries
        self.maximum_interval_between_retries = maximum_interval_between_retries
        self.jitter_up_factor = jitter_up_factor
        self.jitter_down_factor = jitter_down_factor

    def get_next_retry_interval(self, retry_count):
        if self.immediate_first_retry and retry_count == 1:
            return 0
        else:
            random_jitter = self.backoff_interval * random.uniform(
                1 - self.jitter_down_factor, 1 + self.jitter_up_factor
            )
            return min(
                self.minimum_interval_between_retries
                + (pow(2, retry_count - 1) - 1) * random_jitter,
                self.maximum_interval_between_retries,
            )

    def should_retry(self, op, error, retry_count):
        return type(error) in self.retry_error_list


class DefaultExponentialBackoff(ExponentialBackoffWithJitter):
    """
    Backoff interval (c): 100 ms by default.
    Minimal interval between each retry (cMin). 100 milliseconds by default
    Maximum interval between each retry (cMax). 10 seconds by default
    Jitter up factor (Ju). 0.25 by default.
    Jitter down factor (Jd). 0.5 by default
    """

    def __init__(self, retry_error_list):
        super(DefaultExponentialBackoff, self).__init__(
            retry_error_list=retry_error_list,
            immediate_first_retry=True,
            backoff_interval=0.1,
            minimum_interval_between_retries=0.1,
            maximum_interval_between_retries=10,
            jitter_up_factor=0.25,
            jitter_down_factor=0.5,
        )
