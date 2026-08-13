"""If this fails, nothing else in CI matters - the package doesn't even import."""

import meridian


def test_package_imports():
    assert meridian is not None
