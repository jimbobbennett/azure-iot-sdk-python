# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains abstract classes for the various clients of the Azure IoT Hub Device SDK
"""

import logging
import random
from .abstract_redo_policy import AbstractRedoPolicy

logger = logging.getLogger(__name__)


class ExponentialBackoffWithJitter(AbstractRedoPolicy):
    """
     Implements an Exponential Backoff with Jitter retry strategy.
     The function to calculate the next interval is the following:

     F(x) = min(Cmin+ (2^(x-1)-1) * rand(C * (1–Jd), C * (1+Ju)), Cmax)

     Where:
     x = error count (1 after first failure, 2 after second, etc)
     C = backoff interval
     Jd = jitter down percentage
     Ju = jitter up percentage
     Cmin = minimum redo interval
     Cmax = maximum redo interval
    """

    def __init__(
        self,
        redo_op_list,
        redo_error_list,
        immediate_first_redo,
        backoff_interval,
        minimum_interval_between_redos,
        maximum_interval_between_redos,
        jitter_up_factor,
        jitter_down_factor,
    ):
        self.redo_error_list = list(redo_error_list)
        self.redo_op_list = list(redo_op_list)
        self.immediate_first_redo = immediate_first_redo
        self.backoff_interval = backoff_interval
        self.minimum_interval_between_redos = minimum_interval_between_redos
        self.maximum_interval_between_redos = maximum_interval_between_redos
        self.jitter_up_factor = jitter_up_factor
        self.jitter_down_factor = jitter_down_factor

    def get_next_redo_interval(self, redo_count):
        if self.immediate_first_redo and redo_count == 1:
            return 0
        else:
            random_jitter = self.backoff_interval * random.uniform(
                1 - self.jitter_down_factor, 1 + self.jitter_up_factor
            )
            return min(
                self.minimum_interval_between_redos + (pow(2, redo_count - 1) - 1) * random_jitter,
                self.maximum_interval_between_redos,
            )

    def should_redo(self, op, error, redo_count):
        # op and error can both be None.  Only check list membership if we have a value for these.
        if op and type(op) not in self.redo_op_list:
            return False
        if error and type(error) not in self.redo_error_list:
            return False
        return True


class DefaultExponentialBackoff(ExponentialBackoffWithJitter):
    """
    Backoff interval (c): 100 ms by default.
    Minimal interval between each redo (cMin). 100 milliseconds by default
    Maximum interval between each redo (cMax). 10 seconds by default
    Jitter up factor (Ju). 0.25 by default.
    Jitter down factor (Jd). 0.5 by default
    """

    def __init__(self, redo_op_list, redo_error_list):
        super(DefaultExponentialBackoff, self).__init__(
            redo_op_list=redo_op_list,
            redo_error_list=redo_error_list,
            immediate_first_redo=True,
            backoff_interval=0.1,
            minimum_interval_between_redos=0.1,
            maximum_interval_between_redos=10,
            jitter_up_factor=0.25,
            jitter_down_factor=0.5,
        )
