'''import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, CallbackContext

# ضع هنا التوكن الذي حصلت عليه من BotFather
TELEGRAM_TOKEN = '7602342420:AAEBvI7x5c8tgwlw5qQG8Q9lFgUa8Z7-sco'

# ضع هنا الـ API Key الخاص بـ Gemini
GEMINI_API_KEY = 'AIzaSyD9xtSvP629ZS5EgUyCfS_uKy5Z6uvLq54'

# دالة للاستعلام إلى Gemini API
def ask_gemini(question: str) -> str:
    url = "https://gemini.googleapis.com/v1beta/generateText"  # هذا هو الرابط المبدئي ويمكن تغييره حسب توجيهات Gemini API
    headers = {
        'Authorization': f'Bearer {GEMINI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "prompt": question,
        "max_output_tokens": 100,  # عدد الرموز في الإجابة، يمكنك تعديله حسب الحاجة
        "temperature": 0.7,
    }
    
    # إرسال الطلب إلى Gemini API
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        # استخراج الإجابة من الاستجابة
        return result.get("text", "لم أتمكن من الحصول على إجابة.")
    else:
        return "حدث خطأ أثناء الاتصال بـ Gemini."

# دالة الرد على الرسائل
def respond_to_user(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    answer = ask_gemini(user_message)
    update.message.reply_text(answer)

def main():
    # إنشاء الـ Updater مع التوكن الخاص بتلجرام
    updater = Updater(TELEGRAM_TOKEN)

    # الحصول على الـ Dispatcher
    dispatcher = updater.dispatcher

    # إضافة معالج للرسائل
    dispatcher.add_handler(MessageHandler(filters.text & ~filters.command, respond_to_user))

    # بدء البوت
    updater.start_polling()

    # إبقاء البوت يعمل
    updater.idle()

if __name__ == '__main__':
    main()
'''
import os
from dotenv import load_dotenv
import google.generativeai as genai
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler
)

# تحميل المفاتيح من ملف .env
load_dotenv()

# تكوين المفاتيح
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
CHANNEL_USERNAME = "Yemeni_AI_Team"  # تم استخراج اليوزرنيم من الرابط مباشرةً

async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = await context.bot.get_chat_member(
            chat_id=f"@{CHANNEL_USERNAME}",  # استخدام اليوزرنيم مع @
            user_id=user_id
        )
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        print(f"خطأ في التحقق من الاشتراك: {e}")
        return False

async def send_subscription_message(chat_id: int, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة الاشتراك مع أزرار مخصصة"""
    keyboard = [
        [InlineKeyboardButton("الاشتراك في القناة", url=f"https://t.me/{CHANNEL_USERNAME}")],
        [InlineKeyboardButton("✅ تحقق من الاشتراك", callback_data="check_subscription")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_message(
        chat_id=chat_id,
        text="⚠️ يجب الاشتراك في قناة الفريق أولاً\nقناة الفريق: @Yemeni_AI_Team",
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await is_subscribed(user_id, context):
        await update.message.reply_text("مرحبًا! أنا بوت تابع  للفريق اليمني للذكاء الاصطناعي. اسألني أي شيء 🚀")
    else:
        await send_subscription_message(update.effective_chat.id, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await is_subscribed(user_id, context):
        await send_subscription_message(update.effective_chat.id, context)
        return
    
    try:
        user_input = update.message.text
        response = model.generate_content(user_input)
        await update.message.reply_text(response.text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("عذرًا، حدث خطأ تقني. الرجاء المحاولة لاحقًا.")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "check_subscription":
        if await is_subscribed(query.from_user.id, context):
            await query.edit_message_text("🎉 تم التحقق! يمكنك استخدام البوت الآن.")
        else:
            await query.edit_message_text("❌ لم تشترك بعد! الرجاء الاشتراك أولاً:")
            await send_subscription_message(query.message.chat_id, context)

if __name__ == "__main__":
    # تهيئة البوت
    app = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
    
    # إضافة ال handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # بدء التشغيل
    print("البوت يعمل بنجاح...")
    app.run_polling()