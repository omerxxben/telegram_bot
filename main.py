import os
import threading

from flask import Flask

from Telegram.telegram_bot_manager import TelegramBotManager
app = Flask(__name__)


def main() -> None:
    bot_token = "7873230963:AAH0Z1rAPqLlqvXMzpYasR8NMyk4qPn-ANY"
    bot = TelegramBotManager(bot_token)
    bot.run()


if __name__ == '__main__':
    main()

if __name__ == '__main__':
    threading.Thread(target=main).start()
    port = int(os.environ.get("PORT", 10000))  # Render provides $PORT
    app.run(host='0.0.0.0', port=port)