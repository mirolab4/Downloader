import os
import re
import requests
from bs4 import BeautifulSoup
from pytube import YouTube
import telebot

# استبدال 'YOUR_TELEGRAM_BOT_TOKEN' برمز البوت الخاص بك
BOT_TOKEN = "7990298383:AAGLw9yIkYG28Q3pgguEKP7kBIQVjbRgC7I"
bot = telebot.TeleBot(BOT_TOKEN)

# إنشاء مجلد لتخزين الفيديوهات والصور مؤقتًا
if not os.path.exists("downloads"):
    os.makedirs("downloads")

# دالة تنزيل الفيديو من YouTube
def download_youtube_video(url):
    yt = YouTube(url)
    video_stream = yt.streams.filter(file_extension='mp4').first()
    video_path = video_stream.download(output_path="downloads")
    return video_path

# دالة تنزيل الفيديو من TikTok
def download_tiktok_video(url):
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
    
    video_path = "downloads/tiktok_video.mp4"
    video_response = requests.get(video_url, headers=headers)
    with open(video_path, "wb") as f:
        f.write(video_response.content)
    return video_path

# دالة تنزيل المحتوى (فيديو أو صورة) من Twitter
def download_twitter_media(url):
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
    
    # تنزيل المحتوى
    media_path = f"downloads/twitter_{media_type}.{'mp4' if media_type == 'video' else 'jpg'}"
    media_response = requests.get(media_url, headers=headers)
    with open(media_path, "wb") as f:
        f.write(media_response.content)
    
    return media_path, media_type

# دالة البدء
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, 'مرحبًا! أرسل لي رابط الفيديو أو الصورة من YouTube أو TikTok أو Twitter وسأقوم بتنزيله لك.')

# دالة التعامل مع الرسائل النصية
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    url = message.text
    if 'youtube.com' in url or 'youtu.be' in url:
        try:
            bot.reply_to(message, "جارٍ تنزيل الفيديو من YouTube...")
            video_path = download_youtube_video(url)
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            os.remove(video_path)
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ أثناء تنزيل الفيديو: {e}")
    elif 'tiktok.com' in url:
        try:
            bot.reply_to(message, "جارٍ تنزيل الفيديو من TikTok...")
            video_path = download_tiktok_video(url)
            with open(video_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file)
            os.remove(video_path)
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ أثناء تنزيل الفيديو: {e}")
    elif 'twitter.com' in url:
        try:
            bot.reply_to(message, "جارٍ تنزيل المحتوى من Twitter...")
            media_path, media_type = download_twitter_media(url)
            if media_type == 'video':
                with open(media_path, 'rb') as video_file:
                    bot.send_video(message.chat.id, video_file)
            elif media_type == 'photo':
                with open(media_path, 'rb') as photo_file:
                    bot.send_photo(message.chat.id, photo_file)
            os.remove(media_path)
        except Exception as e:
            bot.reply_to(message, f"حدث خطأ أثناء تنزيل المحتوى: {e}")
    else:
        bot.reply_to(message, "الرابط غير مدعوم. يرجى إرسال رابط فيديو أو صورة من YouTube أو TikTok أو Twitter.")

# تشغيل البوت
if __name__ == '__main__':
    print("البوت يعمل...")
    bot.polling()
