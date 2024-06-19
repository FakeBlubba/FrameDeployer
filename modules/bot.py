import os
import time
from resource_manager import ResourceManager
from file_manager import delete_files_except_mp4, delete_folder
from editing import create_video_with_data
from telegram import Bot
from telegram.error import TelegramError
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv(dotenv_path='data/var.env')
TELEGRAM_BOT_TOKEN = os.getenv("tg")

bot_name = 'FrameDeployerBot'
users_interested = set()

def check_status():
    print(f'The {bot_name} is operational!')

async def display_informations(update, context):  
    info = f'''Hi, I am {bot_name}. Here to keep you updated with the top trends!

I guess you want to know the currently available commands (if not, stop spamming "/help").

*Commands*:
🚀 /start: Check the status of the bot.
📹 /sendVideos: Register to receive trending videos every 4 hours.'''
    await update.message.reply_text(info, parse_mode='MarkdownV2')

async def send_videos_command(update, context):
    chat_id = update.effective_chat.id
    users_interested.add(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="You will receive trending videos every 4 hours.")
    
    # Send videos for the first 5 trend numbers immediately
    for trend_number in range(5):
        resource_manager = ResourceManager(trend_number)
        output = resource_manager.generate_resources()
        if output:
            create_video_with_data(output)
            delete_files_except_mp4(output["dir"])
            description_text = f"```{output['Description']}\n\n🎵 Music: {output['MusicPath']['cc']}\n\n\n{output['Tags']}```"
            video_path = os.path.join(output['dir'], "video.mp4")
            if video_path:
                try:
                    await context.bot.send_video(chat_id=chat_id, video=open(video_path, 'rb'), caption=description_text, parse_mode='MarkdownV2')
                    time.sleep(10)
                except TelegramError as e:
                    print(f"Error sending video to Telegram: {e}")
                finally:
                    # Delete the directory after sending the video
                    delete_folder(output['dir'])

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I will send you trending videos every 4 hours.")

def start_bot():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    check_status()
    
    # Register handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('sendVideos', send_videos_command))
    application.add_handler(CommandHandler('info', display_informations))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    start_bot()
