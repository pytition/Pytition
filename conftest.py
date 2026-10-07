"""
Pytest configuration and fixtures for Pytition tests.
"""
import pytest
import django
from django.conf import settings


# Pytest hooks pre lepší výpis
def pytest_collection_modifyitems(config, items):
    """Automaticky pridaj markers na základe názvov testov."""
    for item in items:
        if "mock" in item.name.lower() or "Mock" in item.parent.name:
            item.add_marker(pytest.mark.mock)
        if "stub" in item.name.lower() or "Stub" in item.parent.name:
            item.add_marker(pytest.mark.stub)
        if "fake" in item.name.lower() or "Fake" in item.parent.name:
            item.add_marker(pytest.mark.fake)


def pytest_report_header(config):
    """Pridaj custom header do pytest výstupu."""
    return [
        "=" * 50,
        "Pytition Test Suite",
        "=" * 50,
    ]
