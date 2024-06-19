import time
from datetime import datetime, timedelta
from modules.resource_manager import ResourceManager
import os
from telegram import Bot
from telegram.error import TelegramError, TimedOut, BadRequest
from telegram.ext import Application, CommandHandler, JobQueue, CallbackContext
from dotenv import load_dotenv

load_dotenv(dotenv_path='data/var.env')
TELEGRAM_BOT_TOKEN = os.getenv("tg")

bot_name = 'FrameDeployerBot'
users_interested = set()

def check_status_command(update, context):
    update.message.reply_text('The bot is operational!')

def display_informations(update, context):  
    info = f'''Hi, I am {bot_name}. Here to keep you updated with the top trends!

I guess you want to know the currently available commands (if not, stop spamming "/help").

*Commands*:
🚀 /start: Check the status of the bot.
📹 /sendVideos: Register to receive trending videos every 4 hours.'''
    update.message.reply_text(info, parse_mode='MarkdownV2')

def send_video_to_telegram(bot: Bot, chat_id: str, video_path: str, description_text: str) -> bool:
    try:
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id=chat_id, video=video, caption=f"```\n{description_text}\n```", parse_mode='Markdown')
        return True
    except TelegramError as e:
        print(f"Error sending video to Telegram: {e}")
        return False

def send_videos(context: CallbackContext):
    bot = context.bot
    resource_manager = ResourceManager()
    
    top_trends = resource_manager.get_top_trends(5)
    
    for trend in top_trends:
        output = resource_manager.generate_resources(trend)
        if output:
            video_path = resource_manager.create_video_with_data(output)
            if video_path:
                for chat_id in users_interested:
                    send_video_to_telegram(bot, chat_id, video_path, output['Description'])
                    time.sleep(2)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I will send you trending videos every 4 hours.")

def send_videos_command(update, context):
    chat_id = update.effective_chat.id
    users_interested.add(chat_id)
    context.bot.send_message(chat_id=chat_id, text="You will receive trending videos every 4 hours.")

def start_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('sendVideos', send_videos_command))
    application.add_handler(CommandHandler('info', display_informations))

    # Create JobQueue and schedule jobs
    job_queue = JobQueue()
    job_queue.set_application(application)
    job_queue.run_repeating(send_videos, interval=4 * 60 * 60, first=0)

    # Start the bot
    application.run_polling()
