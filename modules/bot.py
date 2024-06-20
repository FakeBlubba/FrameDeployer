import os
import time
from datetime import datetime, timedelta
from modules.resource_manager import ResourceManager
from modules.file_manager import delete_files_except_mp4, delete_folder
from modules.editing import create_video_with_data
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv(dotenv_path='data/var.env')
TELEGRAM_BOT_TOKEN = os.getenv("tg")

bot_name = 'FrameDeployerBot'

def check_status():
    print(f'The {bot_name} is operational!')

async def display_informations(update, context):  
    """
    Sends a message to the user with the bot's information and available commands.
    
    Args:
    - update: The update object that contains information about the incoming update.
    - context: The context object that contains information about the current context.
    """
    info = f'''Hi, I am {bot_name}. Here to keep you updated with the top trends!

I guess you want to know the currently available commands (if not, stop spamming "/help").

**Commands**:
🚀 /start: Check the status of the bot.
📹 /send_videos: Send videos on the first 5 trends.'''
    escaped_info = escape_markdown_v2(info)
    await update.message.reply_text(escaped_info, parse_mode='MarkdownV2')

def escape_markdown_v2(text):
    """
    Escapes reserved characters in MarkdownV2 mode.

    Args:
    - text (str): The text to be escaped.

    Returns:
    - str: The escaped text.
    """
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join([f'\\{char}' if char in escape_chars else char for char in text])

async def send_videos_command(update, context):
    chat_id = update.effective_chat.id
    number = 5
    await context.bot.send_message(chat_id=chat_id, text=f"I will send you {number} videos, please wait...")
    
    for trend_number in range(number):
        resource_manager = ResourceManager(trend_number)
        await context.bot.send_message(chat_id=chat_id, text=f"I am producing {trend_number + 1}/{number} right now...")

        output = resource_manager.generate_resources()
        if output:
            create_video_with_data(output)
            delete_files_except_mp4(output["Dir"])
            description_text = f"```{output['Description']}\n\n🎵 Music: {output['MusicPath']['cc']}\n\n\n{output['Tags']}```"
            video_path = os.path.join(output['dir'], "video.mp4")
            if video_path:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=open(video_path, 'rb'), caption=description_text, parse_mode='MarkdownV2')
                    time.sleep(10)
                except TelegramError as e:
                    print(f"Error sending video to Telegram: {e}")
                finally:
                    delete_folder(output['dir'])

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Hi I am FrameDeployerBot, if you want /help ask for it!")

def start_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    check_status()
    
    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('send_videos', send_videos_command))
    application.add_handler(CommandHandler('help', display_informations))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    start_bot()
