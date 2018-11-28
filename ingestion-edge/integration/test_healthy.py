# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, you can obtain one at http://mozilla.org/MPL/2.0/.

import gzip
import pytest

# TODO handle use_flush


@pytest.mark.parametrize("data", [b"", b"data", gzip.compress(b"data")])
@pytest.mark.parametrize("headers", [{"header": ""}, {}])
def test_submit_success(data, headers, expect):
    expect.submit(data=data, headers=headers)
    expect.messages(data=data, **headers)


@pytest.mark.parametrize(
    "data,headers,uri",
    [
        (b"almost too long", {}, "/submit/test/"),  # data
        (b"", {"host": "almost too long"}, "/submit/test"),  # host
        (b"", {}, "/submit/test/" + "almost too long"),  # uri
        (b"", {}, "/submit/test?v=" + "almost too long"),  # query string
        (b"", {"header": "almost too long"}, "/submit/test"),  # optional attribute
    ],
)
def test_submit_success_almost_too_long(data, headers, uri, expect):
    expect.submit(data=data, headers=headers, uri=uri)
    expect.messages(data=data, uri=uri, **headers)


@pytest.mark.parametrize(
    "data,headers,uri",
    [
        # invalid data
        (b"too long", {}, "/submit/test"),
        # invalid required attribute
        (b"almost too long", {"host": "almost too long"}, "/submit/test"),  # host
        (b"almost too long", {}, "/submit/test/" + "almost too long"),  # uri
        (b"almost too long", {}, "/submit/test?v=" + "almost too long"),  # args
        # invalid optional attribute
        (b"almost too long", {"header": "almost too long"}, "/submit/test"),
        # invalid whole message
        (
            b"almost too long",
            {"header": "almost too long"},
            "/submit/test/" + "almost too long",
        ),
        # TODO add test where any two elements would be valid but combined is invalid
    ],
)
def test_submit_invalid_payload_too_large(data, headers, uri, expect):
    expect.submit(data=data, headers=headers, uri=uri, status=413)
    expect.messages(count=0)


def test_submit_invalid_uri_too_long(data, headers, uri, expect):
    expect.submit(uri="/submit/test/" + "too long", status=414)
    expect.messages(count=0)
