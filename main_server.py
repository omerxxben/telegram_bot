from Classes.GLOBAL_CONST import BOT_TOKEN
from Telegram.telegram_bot_manager import TelegramBotManager


def main() -> None:
    bot = TelegramBotManager(BOT_TOKEN)
    bot.run()


if __name__ == '__main__':
    main()
