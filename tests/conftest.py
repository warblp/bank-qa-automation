import os
import logging
from datetime import datetime

import pytest
from selenium import webdriver


def pytest_configure(config):
    """Настройка логирования всех тестовых прогонов в logs/test.log"""
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "test.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


@pytest.fixture
def driver(request):
    """Фикстура WebDriver: создаёт браузер, делает скриншот при падении теста."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    yield driver

    if request.node.rep_call.failed:
        screenshot_dir = "screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = os.path.join(screenshot_dir, f"failure_{timestamp}.png")
        driver.save_screenshot(file_path)
        logging.error(f"❌ Скриншот ошибки сохранён: {file_path}")

    driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Сохраняет результат каждого этапа теста (setup/call/teardown) для conftest.driver."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
