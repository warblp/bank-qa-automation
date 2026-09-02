"""
Telegram-бот для удалённого запуска тестов и получения отчётности.

Возможности:
- принимает .py файл с тестами и прогоняет его в изолированном Docker-контейнере;
- принимает вебхук от GitLab CI/CD (job notify_telegram) и пересылает статус пайплайна
  пользователю по запросу.

Токен бота и chat_id НЕ хранятся в коде — берутся из переменных окружения
(см. .env.example в корне репозитория).
"""
import os
import tempfile
import subprocess
import threading

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from fastapi import FastAPI, Request
import uvicorn

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv не обязателен в проде — переменные окружения задаются платформой

TOKEN = os.environ["TG_BOT_TOKEN"]
YOUR_TELEGRAM_CHAT_ID = int(os.environ["TG_CHAT_ID"])
DOCKER_IMAGE = "python:3.11"

bot = Bot(token=TOKEN)
app = FastAPI()
latest_gitlab_message = "❕ Уведомлений от GitLab пока нет"


# ---------- Вебхук от GitLab CI/CD ----------

@app.post("/gitlab")
async def receive_gitlab_update(request: Request):
    """GitLab (job notify_telegram) присылает сюда статус пайплайна."""
    global latest_gitlab_message
    data = await request.json()
    message = data.get("text", "❔ Нет текста от GitLab")
    latest_gitlab_message = message
    await bot.send_message(chat_id=YOUR_TELEGRAM_CHAT_ID, text=message, parse_mode=ParseMode.MARKDOWN)
    return {"ok": True}


# ---------- Прогон присланного файла тестов в Docker ----------

async def run_docker_tests(file_path: str) -> str:
    """Запускает присланный .py файл с тестами в одноразовом Docker-контейнере."""
    try:
        dir_path = os.path.dirname(file_path)
        filename = os.path.basename(file_path)

        cmd = [
            "docker", "run", "--rm",
            "-v", f"{dir_path}:/app",
            "-w", "/app",
            "--memory=512m",
            "--cpus=1",
            DOCKER_IMAGE,
            "bash", "-c",
            f"pip install selenium pytest && pytest {filename}",
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=120)

        if result.returncode == 0:
            return f"✅ Тесты пройдены!\n\n{result.stdout}"
        else:
            error_msg = result.stderr or result.stdout
            return f"❌ Ошибка:\n{error_msg}"

    except subprocess.TimeoutExpired:
        return "🕒 Тесты превысили лимит времени"
    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"


# ---------- Обработчики команд и кнопок ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    button = KeyboardButton("Начать")
    reply_markup = ReplyKeyboardMarkup([[button]], resize_keyboard=True)
    await update.message.reply_text(
        "Нажмите кнопку 'Начать' для продолжения", reply_markup=reply_markup
    )


async def handle_start_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu(update.message)


async def show_main_menu(message):
    buttons = [
        [KeyboardButton("Сделать тест")],
        [KeyboardButton("Получить уведомления GitLab")],
    ]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await message.reply_text("Выберите действие:", reply_markup=reply_markup)


async def handle_test_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Отправьте .py файл с тестами")


async def handle_gitlab_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(latest_gitlab_message, parse_mode=ParseMode.MARKDOWN)
    await show_main_menu(update.message)


async def handle_python_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.document:
        return

    file = await update.message.document.get_file()
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        await file.download_to_drive(tmp.name)
        output = await run_docker_tests(tmp.name)

    os.unlink(tmp.name)
    await update.message.reply_text(output)
    await show_main_menu(update.message)


# ---------- Запуск бота и вебхук-сервера ----------

def run_telegram():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Text(["Начать"]), handle_start_button))
    application.add_handler(MessageHandler(filters.Text(["Сделать тест"]), handle_test_choice))
    application.add_handler(
        MessageHandler(filters.Text(["Получить уведомления GitLab"]), handle_gitlab_choice)
    )
    application.add_handler(MessageHandler(filters.Document.FileExtension("py"), handle_python_file))

    application.run_polling()


def run_webhook():
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    threading.Thread(target=run_telegram).start()
    threading.Thread(target=run_webhook).start()
