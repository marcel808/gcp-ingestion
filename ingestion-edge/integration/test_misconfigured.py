# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

import pytest


@pytest.mark.skip("not implemented")
def test_submit_pubsub_host_unreachable(expect):
    # TODO firewall deny pubsub
    expect.pubsub_failure()
    # TODO firewall allow pubsub
    expect.pubsub_recovery()


@pytest.mark.skip("not implemented")
def test_submit_pubsub_topic_forbidden(expect):
    # TODO pubsub deny topic
    expect.pubsub_failure()
    # TODO pubsub allow topic
    expect.pubsub_recovery()


def test_submit_pubsub_topic_missing(expect):
    publisher = PublisherClient()
    subscriber = SubscriberClient()
    subscriber.delete_subscription(expect.subscription)
    publisher.delete_topic(expect.topic)
    try:
        expect.pubsub_failure()
    finally:
        publisher.create_topic(expect.topic)
        subscriber.create_subscription(expect.subscription, expect.topic)
    expect.pubsub_recovery()
