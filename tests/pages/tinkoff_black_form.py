"""
Page Object для формы оформления дебетовой карты Tinkoff Black.
Все локаторы и действия со страницей собраны здесь — тест (test_tinkoff_form.py)
описывает только сценарий, а не детали DOM.
"""
from selenium.webdriver.common.by import By

from .base_page import BasePage


class TinkoffBlackFormPage(BasePage):
    URL = (
        "https://www.tinkoff.ru/cards/debit-cards/tinkoff-black/"
        "?internal_source=home_main_block_button#form"
    )

    # Локаторы
    FIO_INPUT = (By.NAME, "fio")
    PHONE_INPUT = (By.NAME, "phone_mobile")
    EMAIL_INPUT = (By.NAME, "email")
    BIRTHDATE_INPUT = (By.NAME, "birthdate")
    CITIZENSHIP_YES_LABEL = (By.XPATH, "//div[contains(text(), 'Да')]/ancestor::label")
    OVERLAY = (By.CSS_SELECTOR, "ul.abVxL4--mD")
    SUBMIT_BUTTON = (By.XPATH, "//button[contains(., 'Оформить')]")

    def open_form(self):
        self.open(self.URL)
        return self

    def fill_fio(self, fio: str):
        self.type_text(self.FIO_INPUT, fio)
        return self

    def fill_phone(self, phone: str):
        self.type_text(self.PHONE_INPUT, phone)
        return self

    def fill_email(self, email: str):
        self.type_text(self.EMAIL_INPUT, email)
        return self

    def fill_birthdate(self, birthdate: str):
        self.type_text(self.BIRTHDATE_INPUT, birthdate)
        return self

    def confirm_citizenship_rf(self):
        """Выбрать 'Да' в вопросе о гражданстве РФ, обходя возможный оверлей поверх лейбла."""
        self.wait_invisible(self.OVERLAY)
        self.click_via_js(self.CITIZENSHIP_YES_LABEL)
        return self

    def fill_full_form(self, fio: str, phone: str, email: str, birthdate: str):
        """Заполнить всю форму одним вызовом — удобно для happy-path теста."""
        return (
            self
            .fill_fio(fio)
            .fill_phone(phone)
            .fill_email(email)
            .fill_birthdate(birthdate)
            .confirm_citizenship_rf()
        )

    def is_submit_enabled(self) -> bool:
        return self.find_clickable(self.SUBMIT_BUTTON).is_enabled()
