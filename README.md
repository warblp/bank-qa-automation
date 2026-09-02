# Автоматизация тестирования веб-приложения: Selenium + Pytest + GitLab CI/CD + Telegram-бот

Проект по мотивам выпускной квалификационной работы бакалавра «Анализ и автоматизация
процесса тестирования программного обеспечения». Объединяет в себе
автотесты, CI/CD-пайплайн и телеграм-бота — как единый рабочий процесс, а не набор
разрозненных скриптов.

**Кейс:** автотест формы оформления дебетовой карты Tinkoff Black на сайте Т-Банка.

## Что здесь есть

|Модуль|Что делает|
|-|-|
|[`tests/`](tests)|UI-автотест на Selenium + Pytest в Page Object Model, фикстуры, логирование, скриншот при падении|
|[`tests/pages/`](tests/pages)|Page Object'ы: `BasePage` с общими обёртками над ожиданиями, `TinkoffBlackFormPage` с локаторами и действиями формы|
|[`.gitlab-ci.yml`](.gitlab-ci.yml)|Пайплайн: тест → Allure-отчёт → уведомление в Telegram → публикация на GitLab Pages|
|[`telegram-bot/`](telegram-bot)|Бот: принимает .py-файл с тестами и гоняет его в Docker; получает вебхук от GitLab и отдаёт статус пайплайна по кнопке|
|[`cost-analysis/`](cost-analysis)|Расчёт и визуализация экономии от автоматизации (250 тестов / 234 прогона)|
|[`examples/`](examples)|Простой unittest-файл — пример того, что можно прислать боту на проверку|

## Стек

Python · Selenium WebDriver · Pytest · Allure Report · Docker · GitLab CI/CD ·
python-telegram-bot · FastAPI · pandas / matplotlib

## Как это работает вместе

1. Разработчик пушит код → GitLab CI запускает стадию `test` (Selenium в контейнере `selenium/standalone-chrome`).
2. Стадия `report` собирает результаты в Allure-отчёт и публикует его на GitLab Pages (стадия `pages`).
3. Стадия `notify` дергает Telegram Bot API и присылает статус пайплайна в чат.
4. Отдельно телеграм-бот (`telegram-bot/bot.py`) умеет принимать `.py`-файл с тестами
прямо в чате и прогонять его в одноразовом Docker-контейнере — полезно для быстрой
проверки без захода в GitLab.

## Запуск локально

```bash
git clone <URL\_твоего\_репозитория>
cd <название\_репозитория>
pip install -r requirements.txt

# Автотесты
pytest tests/ --alluredir=allure-results

# Расчёт затрат
python cost-analysis/calculate\_costs.py
python cost-analysis/visualization.py
```

Для теста нужен установленный **Chrome** и **chromedriver**, совместимый по версии
с браузером (chromedriver в репозиторий не кладётся — он платформозависимый бинарник).

## Настройка бота

```bash
cp .env.example .env
# впиши свой TG\_BOT\_TOKEN и TG\_CHAT\_ID в .env
python telegram-bot/bot.py
```

Токены **не хранятся в коде** — берутся из переменных окружения. Для CI то же самое:
`TG\_BOT\_TOKEN` и `TG\_CHAT\_ID` задаются в GitLab → Settings → CI/CD → Variables (Masked).

## Результаты (из ВКР)

* Автотесты интегрированы в пайплайн, запускаются автоматически при пуше в `main`.
* Автоматизация обходится дешевле ручного тестирования более чем в **2,3 раза**
(2 489 160 ₽ против 5 776 316 ₽ на 234 прогонах).

## Дальнейшее развитие

* Расширение покрытия на другие формы/продукты (по образцу `TinkoffBlackFormPage`).
* Параметризация теста (разные наборы валидных/невалидных данных через `pytest.mark.parametrize`).
* Отдельный CI-джоб для линтинга и статического анализа.



