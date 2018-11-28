# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

from .pubsub_emulator import PubsubClients, PubsubEmulator
from . import util
from typing import Dict

# importing from private module _pytest for types only
import _pytest.config.argparsing
import _pytest.fixtures
import os
import pytest
import requests


def pytest_addoption(parser: _pytest.config.argparsing.Parser):
    parser.addoption(
        "--create-pubsub-resources",
        action="store_true",
        dest="create_pubsub_resources",
        default=False,
        help="Create PubSub resources",
    )
    parser.addoption(
        "--target",
        dest="target",
        default=None,
        help="External ingestion-edge server uri for integration tests with no path"
        " element, e.g. http://web:8080",
    )
    parser.addoption(
        "--use-flush",
        action="store_true",
        dest="flush",
        default=False,
        help="target is a single-instance with the /__flush__ endpoint accessible and"
        " not called automatically",
    )
    parser.addoption(
        "--use-minidns",
        action="store_true",
        dest="minidns",
        default=False,
        help="Use minidns to control dns",
    )
    parser.addoption(
        "--use-pubsub-emulator",
        action="store_true",
        dest="pubsub_emulator",
        default=False,
        help="Use pubsub emulator",
    )
    parser.addoption(
        "--submit-method",
        dest="submit_method",
        default="POST",
        help="HTTP method for submit endpoint tests",
    )
    parser.addoption(
        "--submit-uri",
        dest="submit_uri",
        default="/submit/test",
        help="URI for submit endpoint tests, must allow additional path elements",
    )
    parser.addoption(
        "--submit-topic",
        dest="submit_topic",
        default="test",  # TODO add "projects/<project>/topics/" prefix
        help="Pubsub topic for submit endpoint tests",
    )
    parser.addoption(
        "--submit-subscription",
        dest="submit_subscription",
        default="test",  # TODO add "projects/<project>/subscriptions/" prefix
        help="Pubsub subscription for submit endpoint tests",
    )
    parser.addoption(
        "--no-verify",
        action="store_false",
        dest="verify",
        default=True,
        help="Don't verify SSL certs on target",
    )


@pytest.fixture
def create_pubsub_resources(request: _pytest.fixtures.SubRequest) -> bool:
    return request.config.getoption("create_pubsub_resources")


@pytest.fixture
def pubsub_emulator(use_pubsub_emulator: bool) -> PubsubEmulator:
    if use_pubsub_emulator:
        with PubsubEmulator() as emulator:
            yield emulator


@pytest.fixture
def pubsub_clients(pubsub_emulator: PubsubEmulator) -> Pubsub:
    return PubsubClients(pubsub_emulator)


@pytest.fixture
def requests_session(request: _pytest.fixtures.SubRequest) -> requests.Session:
    session = requests.Session()
    session.verify = request.config.getoption("verify")
    return session


@pytest.fixture
def submit_options(
    create_pubsub_resources: bool,
    pubsub_clients: PubsubClients,
    request: _pytest.fixtures.SubRequest,
) -> Dict[str, str]:
    options = {
        "method": request.config.getoption("submit_method"),
        "subscription": request.config.getoption("submit_pubsub_subscription"),
        "topic": request.config.getoption("submit_pubsub_topic"),
        "uri_prefix": request.config.getoption("submit_uri_prefix"),
    }

    if create_pubsub_resources:
        topic_existed = False
        subscription_existed = False
        try:
            pubsub_clients.publisher.create_topic(options["topic"])
        except AlreadyExists:
            topic_existed = True
        try:
            pubsub_clients.subscriber.create_subscription(
                options["subscription"], options["topic"]
            )
        except AlreadyExists:
            subscription_existed = True

    try:
        yield options
    finally:
        if create_pubsub_resources:
            if subscription_existed:
                pubsub_clients.subscriber.delete_subscription(options["subscription"])
            if topic_existed:
                pubsub_clients.publisher.delete_topic(options["topic"])


@pytest.fixture
def target(request: _pytest.fixtures.SubRequest) -> str:
    # TODO start a target if none specified
    return request.config.getoption("target")


@pytest.fixture
def use_flush(request: _pytest.fixtures.SubRequest) -> bool:
    # TODO handle use_flush in test_healthy.py
    return request.config.getoption("use_flush")


@pytest.fixture
def use_minidns(request: _pytest.fixtures.SubRequest) -> bool:
    return request.config.getoption("use_minidns")


@pytest.fixture
def use_pubsub_emulator(request: _pytest.fixtures.SubRequest) -> bool:
    return request.config.getoption("use_pubsub_emulator")


@pytest.fixture
def expect(
    pubsub_clients: PubsubClients,
    requests_session: requests.Session,
    submit_options: Dict[str, str],
    target: str,
    use_flush: bool,
) -> util.Expect:
    # TODO handle use_flush in util.Expect
    return util.Expect(
        publisher=pubsub_clients.publisher,
        session=requests_session,
        subscriber=pubsub_clients.subscriber,
        target=target,
        use_flush=use_flush,
        **submit_options
    )
