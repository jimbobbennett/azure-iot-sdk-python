# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import logging
from azure.iot.device.common import transport_exceptions
from azure.iot.device.common.pipeline import pipeline_exceptions
from azure.iot.device.common.exponential_backoff import DefaultExponentialBackoff

logger = logging.getLogger(__name__)

reconnect_errors = [
    transport_exceptions.ConnectionFailedError,
    transport_exceptions.ConnectionDroppedError,
]

retry_errors = [pipeline_exceptions.PipelineTimeoutError]


class BasePipelineConfig(object):
    """A base class for storing all configurations/options shared across the Azure IoT Python Device Client Library.
    More specific configurations such as those that only apply to the IoT Hub Client will be found in the respective
    config files.
    """

    def __init__(
        self,
        websockets=False,
        retry_policy=DefaultExponentialBackoff(retry_errors),
        reconnect_policy=DefaultExponentialBackoff(reconnect_errors),
    ):
        """Initializer for BasePipelineConfig

        :param bool websockets: Enabling/disabling websockets in MQTT. This feature is relevant if a firewall blocks port 8883 from use.
        """
        self.websockets = websockets
        self.retry_policy = retry_policy
        self.reconnect_policy = reconnect_policy
