import time
from datetime import datetime, timedelta
import conf
from modules.resource_manager import ResourceManager

from telegram import Bot
from telegram.error import TelegramError, TimedOut, BadRequest
from telegram.ext import Updater, CommandHandler, Job, CallbackContext

def send_video_to_telegram(bot: Bot, chat_id: str, video_path: str, description_text: str) -> bool:
    try:
        with open(video_path, 'rb') as video:
            bot.send_video(chat_id=chat_id, video=video, caption=f"```\n{description_text}\n```", parse_mode='Markdown')
        return True
    except TelegramError as e:
        print(f"Error sending video to Telegram: {e}")
        return False

def send_videos_main():
    bot = Bot(token=conf.TELEGRAM_BOT_TOKEN)
    resource_manager = ResourceManager()
    
    while True:
        try:
            top_trends = resource_manager.get_top_trends(5)
            
            for trend in top_trends:
                output = resource_manager.generate_resources(trend)
                if output:
                    video_path = modules.resource_manager.create_video_with_data(output)
                    if video_path:
                        send_video_to_telegram(bot, conf.chatID, video_path, output['Description'])
                        time.sleep(2)
            
            time.sleep(4 * 60 * 60)
            
        except Exception as e:
            print(f"General error in sending videos process: {e}")
            time.sleep(30)

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome! I will send you trending videos every 4 hours.")

def main():
    updater = Updater(token=conf.TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler('start', start))
    
    job_queue = updater.job_queue
    
    job_queue.run_repeating(send_videos_main, interval=4 * 60 * 60, first=0)
    
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
