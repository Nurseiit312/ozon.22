import os
import django
import requests

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

# Настройка Django окружения
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ozonshop.settings")
django.setup()

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"  # Вставь сюда токен
DJANGO_API_URL = "http://127.0.0.1:8000/api"

def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "Привет! Я бот-магазин.\n"
        "Команды:\n"
        "/products — список товаров\n"
        "/balance — проверить баланс"
    )

def fetch_products():
    try:
        r = requests.get(f"{DJANGO_API_URL}/products/")
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Ошибка запроса товаров: {e}")
        return []

def show_products(update: Update, context: CallbackContext):
    products = fetch_products()
    if not products:
        update.message.reply_text("Товары недоступны :(")
        return

    keyboard = [
        [InlineKeyboardButton(f"{p['name']} — {p['price']}₽", callback_data=f"buy_{p['id']}")]
        for p in products
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Выберите товар для покупки:", reply_markup=reply_markup)

def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    telegram_user_id = query.from_user.id
    username = query.from_user.username or ""
    data = query.data

    if data.startswith("buy_"):
        product_id = int(data.split("_")[1])

        # Регистрируем пользователя (если нет)
        try:
            requests.post(
                f"{DJANGO_API_URL}/telegram-users/",
                json={"telegram_id": telegram_user_id, "username": username}
            )
        except:
            pass  # если пользователь уже есть — игнорируем ошибку

        order_data = {
            "telegram_id": telegram_user_id,
            "items": [{"product": product_id, "quantity": 1}]
        }

        try:
            r = requests.post(f"{DJANGO_API_URL}/orders/", json=order_data)
            if r.status_code == 201:
                query.edit_message_text("✅ Заказ успешно оформлен! Деньги списаны.")
            else:
                # Пытаемся вывести ошибку с сервера, если есть
                try:
                    err = r.json().get("detail") or r.text
                except:
                    err = r.text
                query.edit_message_text(f"❌ Ошибка при заказе: {err}")
        except Exception as e:
            query.edit_message_text(f"⚠️ Ошибка сервера: {e}")

def show_balance(update: Update, context: CallbackContext):
    telegram_user_id = update.effective_user.id
    try:
        r = requests.get(f"{DJANGO_API_URL}/telegram-users/{telegram_user_id}/balance/")
        r.raise_for_status()
        data = r.json()
        balance = data.get("balance", "0.00")
        update.message.reply_text(f"💰 Ваш баланс: {balance}₽")
    except Exception as e:
        update.message.reply_text(f"Ошибка получения баланса: {e}")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("products", show_products))
    dp.add_handler(CommandHandler("balance", show_balance))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
