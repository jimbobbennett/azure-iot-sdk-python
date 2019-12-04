# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""This module contains abstract classes for Azure IoT SDK retry policies
"""

import six
import abc


@six.add_metaclass(abc.ABCMeta)
class AbstractRedoPolicy(object):
    """
    Abstract Base Class which can define either a _retry policy_ or a _reconnect policy_.

    A _retry policy_ is intended to be used when an operation fails for some reason, but the
    connection to the service is known to be good.  The retry policy would be used, for
    instance, if an operation times out, or if an operation is throttled by the server.

    A _reconnect policy_ is intended to be used then an operation fails because the
    connection to the server could not be established, or a previously established connection
    was severed.  The reconnect policy would be used whether the connection failed as the
    result of some specific operation, or because the connection failed spontaneously.

    The distinction between retry policy and reconnect policy exists because we need to treat
    these differently in cases of overlapping operations.  Take the example of sending 5
    events over an unreliable network link. If the events send but the ack never comes back,
    but we know that the connection is still good, we want to re-attempt all 5 of these
    events independently.  If we are waiting to retry one operation, there is no reason
    to wait for the same period of time before retrying a different operation.  This is
    example where the retry policy would be used.

    If, however, the link is so unreliable that the connection closes, we need to reconnect
    before we send or receive anything from the server.  This might need to follow a different
    set of rules than retrying.  In this 5-event example, if we are already waiting to
    reconnect after one operation failed to connect, we might want to wait until the connection
    has been established before even trying for a second operation.  If the pipeline has
    already tried to reconnect 3 times, we want to decide how long to wait before trying to
    reconnect again based on the fact that we've already failed 3 times, even when the client
    is we trying to send new events.

    Another distinction between retry and reconnect is that all ops waiting for reconnection
    will be unblocked once the connection is re-established.  The single event (connection
    established) will unblock all ops waiting for a connection.  For retry, however, each op
    ends up waiting to retry independently.  There is no single event which unblock all ops
    that are waiting to retry.

    When this code is used for a _retry_ policy, the functions on this object gets called
    on a per-operation basis.  So, for example, if there are 2 send_event operations failing
    for the first time, the pipeline will call should_retry() and, maybe, get_next_retry_interval()
    twice, once for each operation, and both times with error_count=1.

    When this code is used for a _reconnect_ policy, functions on this object will get called on a
    per-connection-failure basis.  So, for example, if the client is attempting to send 2 events,
    and the pipeline is unable to connect, should_redo(), and get_next_redo_interval() will
    get called only once called once because the pipeline failed to connect once.  Both events will
    be pended based on this single reconnection.

    The decision on which errors cause a _retry_ versus which errors cause a _reconnect_ is based
    on the should_redo() method on the retry policy and the same method on the reconnect policy.
    If should_redo() on the retry policy object returns True, then the operation is retried based
    on the retry policy.  If, however, should_redo() on the retry policy returns False, but
    should_redo() on the reconnect policy returns True, then the operation is retried based on the
    reconnect policy.

    If the connection gets severed spontaneously, the reconnect policy is used to try re-establishing
    the connection even if the client does not attempt any operations.  In this way, the client
    can be assured that the library is doing it's best to be connected in order to receive service-
    initiated operations (such as direct method calls or C2D Messages).

    The reconnect policy can distinguish between failures caused by client action (such as a
    failed send_event) and spontaneous disconencts (such as a loss of signal) based on the error
    parameter passed to should_redo().  If error=None, that means that the connection dropped, but
    not because of anything the client did.  Using this, the reconnect policy can decide to be
    agressive about reconnecting (to be available to traffic coming from the service) or to be
    less agressive about reconnecting and only reconnect if the client attempts an operation
    (because server-intiated traffic is unexpected or not very important).
    """

    @abc.abstractmethod
    def get_next_redo_interval(self, error_count):
        """
        Computes the interval to wait before redoing an operation.  This function assumes that the
        decision to redo has already been made and it just needs to compute how long to wait
        until redoing the next time.

        When error_count is 1, this method should assume that there was a single failure already
        and it should return how long (in seconds) to wait before trying the operation a second time.
        When error_count is 2, there have already been 2 failures for the specific operation and this
        method should return how long to wait before trying a third time, and so on.

        @param {number} error_count   Count of retries so far, including this one.  Set to 1 for the first error.
        @returns {number}             The time to wait before attempting a redo in seconds
        """
        pass

    @abc.abstractmethod
    def should_redo(self, op, error, error_count):
        """
        Based on the arguments, this function decides if the operation should be retried.  This decision
        can be made based on the specific error that caused the operation failure, the number of retries
        already attempted, or both.

        When error_count is 1, this method should assume that there was a single failure already
        and it should decide if the pipeline should try the operation a second time.  When error_count is
        2, there have already been 2 failures for the specific operation, and this method should decide
        if the pipeline should try the operation a third time, and so on.

        @param {PipelineOperation} op   The operation which failed.
        @param {Error} error            The error encountered by the operation.
        @param {number} error_count     Count of retries so far, including this one.  Set to 1 for the first error.
        @returns {boolean}              Whether the operation should be retried or not.
        """
        pass
