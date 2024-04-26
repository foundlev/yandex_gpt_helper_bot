import requests
import telebot

# Yandex API Tokens
OAUTH_TOKEN: str = ""
FOLDER_ID: str = ""
# Telgram Bot Token
BOT_TOKEN: str = ""


bot = telebot.TeleBot(token=BOT_TOKEN)


def load_iam_token() -> str:
    with open("iam_token.txt", "r") as f:
        return f.read()


def save_iam_token(token: str):
    with open("iam_token.txt", "w") as f:
        f.write(token)


def create_iam_token() -> str:
    p = {
        "yandexPassportOauthToken": OAUTH_TOKEN
    }
    u = "https://iam.api.cloud.yandex.net/iam/v1/tokens"

    return requests.post(u, json=p).json()["iamToken"]


def ask_yandex(question: str, iam_token: str) -> str:
    h = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
        "x-folder-id": str(FOLDER_ID)
    }
    u = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

    p = {
        "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.5,
            "maxTokens": "1000"
        },
        "messages": [
            {
            "role": "user",
            "text": str(question)
            }
        ]
    }

    r = requests.post(u, json=p, headers=h)
    return r.json()["result"]["alternatives"][0]["message"]["text"]


@bot.message_handler()
def func(message):
    if message.chat.id != 6174356474:
        return

    try:
        if message.text == "/start":
            markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = telebot.types.KeyboardButton("🔄 IAM Токен")
            markup.add(btn1)
            bot.send_message(message.chat.id, text="👋 Добро пожаловать. Жду ваших запросов.", reply_markup=markup)

        elif message.text == "🔄 IAM Токен":
            bot.send_message(message.chat.id, "🕒 Выпускаю новый IAM токен")
            new_token = create_iam_token()
            save_iam_token(new_token)
            bot.send_message(message.chat.id, "✅ IAM токен выпущен и сохранен")

        elif message.text:
            bot.send_message(message.chat.id, "⬆️ Запрос формируется")
            iam_token = load_iam_token()
            answer = ask_yandex(message.text, iam_token)
            bot.send_message(message.chat.id, answer, parse_mode="markdown", disable_web_page_preview=True)

        else:
            text = "❌ Не удалось распознать текст"
            bot.send_message(message.chat.id, text)

    except Exception as e:
        text = f"❌ Ошибка: {e}"
        bot.send_message(message.chat.id, text, disable_web_page_preview=True)


if __name__ == "__main__":
    bot.polling(none_stop=True)
