"""Test configuration and fixtures"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from athesa.adapters.selenium import SeleniumBridge
from athesa.events import EventEmitter


@pytest.fixture
def chrome_driver():
    """Provide a Chrome WebDriver instance"""
    options = Options()
    options.add_argument('--headless')  # Run in headless mode for CI
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


@pytest.fixture
def selenium_bridge(chrome_driver):
    """Provide a configured SeleniumBridge"""
    return SeleniumBridge(chrome_driver)


@pytest.fixture
def event_emitter():
    """Provide an EventEmitter instance"""
    return EventEmitter()


@pytest.fixture
def sample_credentials():
    """Provide sample login credentials"""
    return {
        'username': 'test@example.com',
        'password': 'test_password_123'
    }
