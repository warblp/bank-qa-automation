"""
Базовый класс для всех Page Object'ов: общие обёртки над ожиданиями Selenium,
чтобы конкретные страницы не дублировали WebDriverWait/EC в каждом методе.
"""
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class BasePage:
    DEFAULT_TIMEOUT = 20

    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def open(self, url: str):
        self.driver.get(url)
        return self

    def find(self, locator):
        """Дождаться появления элемента и вернуть его."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_clickable(self, locator):
        """Дождаться, пока элемент станет кликабельным, и вернуть его."""
        return self.wait.until(EC.element_to_be_clickable(locator))

    def type_text(self, locator, text: str):
        element = self.find(locator)
        element.send_keys(text)
        return element

    def click_via_js(self, locator):
        """
        Клик через JS вместо element.click() — на форме Tinkoff клики иногда
        перехватываются оверлеем поверх лейбла, обычный click() падает
        с ElementClickInterceptedException.
        """
        element = self.find_clickable(locator)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.driver.execute_script("arguments[0].click();", element)
        return element

    def wait_invisible(self, locator):
        """Дождаться исчезновения элемента (например, оверлея), не падая, если его и не было."""
        try:
            self.wait.until(EC.invisibility_of_element_located(locator))
        except Exception:
            pass
