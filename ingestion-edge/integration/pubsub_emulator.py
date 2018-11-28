# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

from concurrent import futures
from collections import defaultdict
from google.cloud.pubsub import PublisherClient, SubscriberClient
from google.cloud.pubsub_v1.proto import pubsub_pb2_grpc, pubsub_pb2
from time import sleep
from uuid import uuid4
import grpc


class PubsubEmulator(
    pubsub_pb2_grpc.PublisherServicer, pubsub_pb2_grpc.SubscriberServicer
):
    timeout = False
    server_error = False
    publish_error = False

    def __init__(self, port: int = 0):
        # message queue
        self.messages = defaultdict(list)
        # initalize grpc server with pubsub api
        self.new_server(port)
        pubsub_pb2_grpc.add_PublisherServicer_to_server(self, self.server)
        pubsub_pb2_grpc.add_SubscriberServicer_to_server(self, self.server)

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.stop()

    def new_server(self, port: int = 0):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
        self.port = self.server.add_insecure_port("[::]:%d" % port)

    def start(self):
        self.server.start()

    def stop(self):
        self.server.stop(grace=None)

    def Publish(self, request, context):
        if self.timeout:
            sleep(61)  # pubsub client timeout is 60 seconds
        elif self.server_error:
            context.set_code(grpc.StatusCode.SERVER_ERROR)
        elif self.publish_error:
            return pubsub_pb2.PublishResponse(message_ids=[])
        else:
            message_ids = []
            for message in request.messages:
                message.message_id = uuid4().hex
                message_ids.append(message.message_id)
            self.messages[request.topic].extend(request.messages)
            return pubsub_pb2.PublishResponse(message_ids=message_ids)

    # TODO implement Pull
    # TODO implement Acknowledge


class PubsubClients:
    def __init__(self, emulator: PubsubEmulator = None):
        channel = None
        if emulator is not None:
            channel = grpc.insecure_channel(target="localhost:%d" % emulator.port)
        self.publisher = PublisherClient(channel=channel)
        self.subscriber = SubscriberClient(channel=channel)
