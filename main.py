import os
import threading
from flask import Flask
from Telegram.telegram_bot_manager import TelegramBotManager

app = Flask(__name__)

def start_bot():
    bot_token = "7873230963:AAH0Z1rAPqLlqvXMzpYasR8NMyk4qPn-ANY"
    bot = TelegramBotManager(bot_token)
    bot.run()

@app.route('/')
def home():
    return 'Bot is running !'

if __name__ == '__main__':
    # Start the bot in a background thread
    threading.Thread(target=start_bot).start()

    # Bind to the port Render gives us
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
