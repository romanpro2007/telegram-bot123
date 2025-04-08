import telebot
from telebot import types

bot = telebot.TeleBot('7466607506:AAH0L3XVmWX2hutP4SdPPJkSg7OoKR8Skdg')  # ← замени на свой токен

# Данные
cities = {
    "Николаев": ["Центральный", "Ингульский", "Соляные", "Лески", "Намыв", "Корабельный", "Заводской"],
    "Одеса": ["Приморский", "Киевский", "Малиновский", "Суворовский"],
    "Киев": ["Голосеевский", "Оболонь", "Печерский", "Подольский", "Шевченковский", "Соломенский", "Святошинский", "Днепровский", "Дарницкий", "Деснянский"],
    "Запорожье": ["Днепровский", "Комунарский", "Александровский", "Заводский", "Вознесеновский", "Хортицкий", "Шевченковский"]
}

products = {
    district: [
        "Бошки Gagarin 31% -- 300 грн",
        "Бошки Opium 29% -- 290 грн",
        "Бошки Blackberry 25% -- 250 грн",
        "Бошки Tyson 29% -- 270 грн"
    ] for city_districts in cities.values() for district in city_districts
}

product_prices = {
    "Бошки Gagarin 31% -- 300 грн": 300,
    "Бошки Opium 29% -- 290 грн": 290,
    "Бошки Blackberry 25% -- 250 грн": 250,
    "Бошки Tyson 29% -- 270 грн": 270
}

product_images = {
    "Бошки Gagarin 31% -- 300 грн": "./images/gagarin.jpg",
    "Бошки Opium 29% -- 290 грн": "./images/opium.jpg",
    "Бошки Blackberry 25% -- 250 грн": "./images/blackberry.jpg",
    "Бошки Tyson 29% -- 270 грн": "./images/tyson.jpg"
}

gram_options = ["2 грамма", "3 грамма", "5 грамм + 1 грамм(бонус)", "10 грамм + 3 грамма(бонус)", "🔙Назад"]

payment_info = (
    "💳 Для оплаты переведите сумму заказа на карту\n"
    "`4149 5001 1329 8478`\n"
    "и отправьте скриншот чека сюда.\n"
    "Координаты отправляются в течение 15 минут после получения оплаты."
)

user_state = {}

# Универсальная клавиатура с техподдержкой
def add_support_button(markup):
    markup.add(types.KeyboardButton("👨‍💻 Техподдержка"))
    return markup

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for city in cities:
        markup.add(types.KeyboardButton(city))
    add_support_button(markup)
    bot.send_message(message.chat.id, "🏙 Выберите свой город:", reply_markup=markup)

# Обработка техподдержки
@bot.message_handler(func=lambda message: message.text == "👨‍💻 Техподдержка")
def tech_support(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Написать в техподдержку", url="https://t.me/klad99_support"))
    bot.send_message(message.chat.id, "📞 Свяжитесь с оператором по кнопке ниже:", reply_markup=markup)

# Обработка выбора города
@bot.message_handler(func=lambda message: message.text in cities)
def select_city(message):
    user_state[message.chat.id] = {"city": message.text}
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for district in cities[message.text]:
        markup.add(types.KeyboardButton(district))
    add_support_button(markup)
    bot.send_message(message.chat.id, f"📍 Город {message.text} выбран. Теперь выберите район:", reply_markup=markup)

# Обработка выбора района
@bot.message_handler(func=lambda message: any(message.text in d for d in cities.values()))
def select_district(message):
    chat_id = message.chat.id
    if chat_id not in user_state or "city" not in user_state[chat_id]:
        bot.send_message(chat_id, "❗ Сначала выберите город.")
        return
    user_state[chat_id]["district"] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for product in products.get(message.text, []):
        markup.add(types.KeyboardButton(product))
    add_support_button(markup)
    bot.send_message(chat_id, f"📦 Район {message.text} выбран. Выберите товар:", reply_markup=markup)

# Обработка выбора товара
@bot.message_handler(func=lambda message: message.text in product_prices)
def select_product(message):
    chat_id = message.chat.id
    product = message.text
    user_state[chat_id]["product"] = product
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for grams in gram_options:
        markup.add(types.KeyboardButton(grams))
    add_support_button(markup)

    photo_path = product_images.get(product)
    if photo_path:
        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=f"🛒 Вы выбрали: {product}\n💰 Цена за грамм: {product_prices[product]} грн")
    else:
        bot.send_message(chat_id, f"🛒 Вы выбрали: {product}\n💰 Цена за грамм: {product_prices[product]} грн")

    bot.send_message(chat_id, "Выберите количество граммовки:", reply_markup=markup)

# Обработка выбора граммовки
@bot.message_handler(func=lambda message: message.text in gram_options)
def select_grams(message):
    chat_id = message.chat.id

    if message.text == "🔙Назад":
        district = user_state[chat_id].get("district")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for product in products.get(district, []):
            markup.add(types.KeyboardButton(product))
        add_support_button(markup)
        bot.send_message(chat_id, f"📦 Район {district} выбран. Выберите товар:", reply_markup=markup)
        return

    grams = int(message.text.split()[0])
    product = user_state[chat_id]["product"]
    price_per_gram = product_prices[product]
    total = grams * price_per_gram
    user_state[chat_id]["grams"] = grams
    user_state[chat_id]["total"] = total

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("✅ Я оплатил"))
    add_support_button(markup)
    bot.send_message(chat_id, f"💵 Общая сумма: *{total} грн*\n\n{payment_info}", parse_mode='Markdown', reply_markup=markup)

# Обработка оплаты
@bot.message_handler(func=lambda message: message.text == "✅ Я оплатил")
def confirm_payment(message):
    bot.send_message(message.chat.id, "✅ Спасибо за оплату! Мы проверим чек и вскоре отправим координаты.")

# Запуск бота
bot.polling(none_stop=True)
