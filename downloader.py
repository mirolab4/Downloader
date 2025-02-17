import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from pytube import YouTube
import requests
from bs4 import BeautifulSoup

# إعداد التسجيل (Logging)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# دالة تنزيل الفيديو من YouTube وإرساله مباشرة
def send_youtube_video(url, update: Update):
    try:
        yt = YouTube(url)
        video_stream = yt.streams.filter(file_extension='mp4').first()
        video_url = video_stream.url  # الحصول على رابط مباشر للفيديو
        update.message.reply_video(video=video_url)
    except Exception as e:
        update.message.reply_text(f"حدث خطأ أثناء إرسال الفيديو: {e}")

# دالة إرسال الفيديو من TikTok مباشرة
def send_tiktok_video(url, update: Update):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج رابط الفيديو من الصفحة
        video_url = None
        for script in soup.find_all('script'):
            if 'videoData' in script.text:
                match = re.search(r'"playAddr":"(https://[^"]+)"', script.text)
                if match:
                    video_url = match.group(1).replace("\\u002F", "/")
                    break
        
        if not video_url:
            raise Exception("لم يتم العثور على رابط الفيديو.")
        
        update.message.reply_video(video=video_url)
    except Exception as e:
        update.message.reply_text(f"حدث خطأ أثناء إرسال الفيديو: {e}")

# دالة إرسال المحتوى (فيديو أو صورة) من Twitter مباشرة
def send_twitter_media(url, update: Update):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # استخراج رابط الفيديو أو الصورة
        media_url = None
        media_type = None
        
        # البحث عن رابط الفيديو
        video_tag = soup.find("video")
        if video_tag:
            media_url = video_tag['src']
            media_type = 'video'
        else:
            # البحث عن رابط الصورة
            image_tag = soup.find("img", {"alt": "Image"})
            if image_tag:
                media_url = image_tag['src']
                media_type = 'photo'
        
        if not media_url:
            raise Exception("لم يتم العثور على محتوى (فيديو أو صورة).")
        
        if media_type == 'video':
            update.message.reply_video(video=media_url)
        elif media_type == 'photo':
            update.message.reply_photo(photo=media_url)
    except Exception as e:
        update.message.reply_text(f"حدث خطأ أثناء إرسال المحتوى: {e}")

# دالة البدء
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('مرحبًا! أرسل لي رابط الفيديو أو الصورة من YouTube أو TikTok أو Twitter وسأقوم بإرساله لك مباشرة.')

# دالة التعامل مع الرسائل النصية
def handle_message(update: Update, context: CallbackContext) -> None:
    url = update.message.text
    if 'youtube.com' in url or 'youtu.be' in url:
        update.message.reply_text("جارٍ إرسال الفيديو من YouTube...")
        send_youtube_video(url, update)
    elif 'tiktok.com' in url:
        update.message.reply_text("جارٍ إرسال الفيديو من TikTok...")
        send_tiktok_video(url, update)
    elif 'twitter.com' in url:
        update.message.reply_text("جارٍ إرسال المحتوى من Twitter...")
        send_twitter_media(url, update)
    else:
        update.message.reply_text("الرابط غير مدعوم. يرجى إرسال رابط فيديو أو صورة من YouTube أو TikTok أو Twitter.")

# دالة الأخطاء
def error(update: Update, context: CallbackContext) -> None:
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main() -> None:
    # استبدال 'YOUR_TELEGRAM_BOT_TOKEN' برمز البوت الخاص بك
    updater = Updater("YOUR_TELEGRAM_BOT_TOKEN")

    dispatcher = updater.dispatcher

    # إضافة المعالجات
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    # إضافة معالج الأخطاء
    dispatcher.add_error_handler(error)

    # بدء البوت
    updater.start_polling()

    # تشغيل البوت حتى يتم إيقافه يدويًا
    updater.idle()

if __name__ == '__main__':
    main()
