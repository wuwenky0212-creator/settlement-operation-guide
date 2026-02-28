"""Test to verify project setup"""
import pytest
from hypothesis import given, strategies as st


@pytest.mark.unit
def test_config_import():
    """Test that config module can be imported"""
    from app import config
    assert config.settings is not None


@pytest.mark.unit
def test_main_import():
    """Test that main module can be imported"""
    from app import main
    assert main.app is not None


@pytest.mark.unit
def test_database_url_format():
    """Test database URL is correctly formatted"""
    from app.config import settings
    assert "postgresql://" in settings.database_url
    assert settings.database_name in settings.database_url


@pytest.mark.property
@given(st.integers(min_value=1, max_value=100))
def test_hypothesis_setup(value):
    """Test that Hypothesis is properly configured"""
    # Feature: settlement-operation-guide, Property Test Setup
    assert value > 0
    assert value <= 100
