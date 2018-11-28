# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

from google.cloud.pubsub_v1 import PublisherClient
import grpc


def test_pubsub(pubsub):
    client = PublisherClient(channel=grpc.insecure_channel(target=":%d" % pubsub.port))
    messages = [
        {"data": b"data", "attributes": {}},
        {"data": b"", "attributes": {"meta": "data"}},
    ]
    response = client.api.publish("topic", messages, retry=None)
    assert len(messages) == len(pubsub.messages["topic"])
    assert response.message_ids == [
        message.message_id for message in pubsub.messages["topic"]
    ]
    assert messages == [
        {"data": message.data, "attributes": dict(message.attributes)}
        for message in pubsub.messages["topic"]
    ]
