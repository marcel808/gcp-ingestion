# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

import pytest
from subprocess import call


def test_submit_pubsub_dns(minidns, expect):
    if minidns is None:
        pytest.skip("test requires minidns")
    if pubsub_emulator is not None:
        pytest.skip("test requires pubsub host be under googleapis.com")
    if minidns.get_zone("googleapis.com") is None:
        raise Exception(
            "this test requires minidns to own googleapis.com before the target is started"
        )
    expect.pubsub_failure()
    minidns.delete_zone("googleapis.com")
    expect.pubsub_recover()
