import pytest
from selenium import webdriver

from pages.tinkoff_black_form import TinkoffBlackFormPage


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()


def test_tinkoff_black_form_submission(driver):
    """
    Кейс: форма оформления дебетовой карты Tinkoff Black.
    Заполняем обязательные поля корректными данными и проверяем,
    что кнопка "Оформить" становится активной.
    """
    form = TinkoffBlackFormPage(driver).open_form()

    form.fill_full_form(
        fio="Иванов Алексей Петрович",
        phone="9991234567",
        email="test@example.com",
        birthdate="01.01.1990",
    )

    assert form.is_submit_enabled(), (
        "❌ Кнопка 'Оформить' неактивна — форма, возможно, заполнена некорректно."
    )
