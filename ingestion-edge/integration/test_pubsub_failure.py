# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.


def test_submit_pubsub_reject_message(pubsub_emulator, expect):
    if pubsub_emulator is None:
        pytest.skip("requires pubsub emulator")

    pubsub.publish_error = True
    expect.submit(status=400)
    expect.messages(count=0)
    expect.flush(status=204)

    pubsub.publish_error = False
    expect.pubsub_success()


def test_submit_pubsub_timeout(pubsub_emulator, expect):
    if pubsub_emulator is None:
        pytest.skip("requires pubsub emulator")

    pubsub.timeout = True
    expect.pubsub_failure()

    pubsub.timeout = False
    expect.pubsub_recover()


def test_submit_pubsub_not_listening_on_port(pubsub_emulator, expect):
    if pubsub_emulator is None:
        pytest.skip("requires pubsub emulator")

    pubsub.stop()
    expect.pubsub_failure()

    pubsub.new_server(pubsub.port)
    pubsub.start()
    expect.pubsub_recover()


def test_submit_pubsub_server_error(pubsub_emulator, expect):
    if pubsub_emulator is None:
        pytest.skip("requires pubsub emulator")

    pubsub.server_error = True
    expect.pubsub_failure()

    pubsub.server_error = False
    expect.pubsub_recover()


# requires 20MB disk queue
# 20MB is just big enough to not interfere with other tests in this module
def test_submit_pubsub_server_error_disk_full(pubsub_emulator, expect):
    if pubsub_emulator is None:
        pytest.skip("requires pubsub emulator")

    pubsub.server_error = True
    data = b"5MB"
    for i in range(3):
        expect.submit(data=data)
    expect.submit(data=data, status=507)
    expect.flush(status=500, done=0, pending=3)
    expect.submit(method="GET", uri="/__heartbeat__", data=None, status=500, text=None)

    pubsub.server_error = False
    expect.pubsub_recover(count=3, data=data)
    expect.submit(method="GET", uri="/__heartbeat__", data=None, text=None)
