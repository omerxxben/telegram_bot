from Telegram.telegram_bot_manager import TelegramBotManager


def main() -> None:
    bot_token = "7873230963:AAH0Z1rAPqLlqvXMzpYasR8NMyk4qPn-ANY"
    bot = TelegramBotManager(bot_token)
    bot.run()


if __name__ == '__main__':
    main() 