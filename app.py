
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

users = {}

subjects_flow = {
    "Math 3": ["exam", "td"],
    "Electronic": ["exam", "td", "tp"],
    "Electrotechnic": ["exam", "td", "tp"],
    "Propability": ["exam", "td"],
    "Vibration": ["exam", "td", "tp"],
    "Energy": ["exam"],
    "English": ["exam"],
    "Cinétique": ["exam"],
    "Informatique": ["tp"]
}

def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {"subject": None, "step": 0, "data": {}}

    keyboard = [
        ["Math 3", "Vibration"],
        ["Electronic", "Electrotechnic"],
        ["Propability", "Energy"],
        ["English", "Cinétique"],
        ["Informatique"],
        ["📊 احسب المعدل"]
    ]

    update.message.reply_text(
        "اختر المادة 👇",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def select_subject(update, context):
    uid = update.message.from_user.id
    text = update.message.text

    if text == "📊 احسب المعدل":
        calculate(update, context)
        return

    users[uid]["subject"] = text
    users[uid]["step"] = 0
    users[uid]["data"][text] = {}

    ask_next(update, uid)

def ask_next(update, uid):
    subject = users[uid]["subject"]
    step = users[uid]["step"]
    flow = subjects_flow[subject]

    field = flow[step]
    update.message.reply_text(f"✏️ أدخل {field.upper()}")

def save_value(update, context):
    uid = update.message.from_user.id
    if uid not in users or users[uid]["subject"] is None:
        return

    subject = users[uid]["subject"]
    value = float(update.message.text)

    flow = subjects_flow[subject]
    step = users[uid]["step"]
    field = flow[step]

    users[uid]["data"][subject][field] = value
    users[uid]["step"] += 1

    if users[uid]["step"] < len(flow):
        ask_next(update, uid)
    else:
        update.message.reply_text("✅ تم حفظ المادة")
        users[uid]["subject"] = None

def calculate(update, context):
    uid = update.message.from_user.id
    d = users[uid]["data"]

    def td_exam(td, ex): return 0.4 * td + 0.6 * ex

    total, coef = 0, 0

    total += td_exam(d["Math 3"]["td"], d["Math 3"]["exam"]) * 3; coef += 3
    total += td_exam(d["Vibration"]["td"], d["Vibration"]["exam"]) * 2; coef += 2
    total += td_exam(d["Electronic"]["td"], d["Electronic"]["exam"]) * 2; coef += 2
    total += td_exam(d["Electrotechnic"]["td"], d["Electrotechnic"]["exam"]) * 2; coef += 2
    total += td_exam(d["Propability"]["td"], d["Propability"]["exam"]) * 2; coef += 2

    total += d["Energy"]["exam"]; coef += 1
    total += d["English"]["exam"]; coef += 1
    total += d["Cinétique"]["exam"]; coef += 1

    total += d["Informatique"]["tp"]; coef += 1
    total += d["Vibration"]["tp"]; coef += 1
    total += (d["Electronic"]["tp"] + d["Electrotechnic"]["tp"]) / 2; coef += 1

    avg = total / coef

    if avg < 10:
    context.bot.send_video(
        chat_id=update.message.chat_id,
        video="BAACAgQAAxkBAAEaodRpgeMsuRlspccGXp3oR0zgqtBbtgACExwAAmV0EFApFTsxOBuR6jgE",
        caption="😅 معدلك أقل من 10، شد حيلك!"
    )
else:
    update.message.reply_text("🎉 مبروك! ناجح")

    user = update.message.from_user
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "لا يوجد"

    report = f"👤 الاسم: {name}\n🔗 المستخدم: {username}\n📊 المعدل = {avg:.2f}"
    context.bot.send_message(chat_id=ADMIN_ID, text=report)

    update.message.reply_text(f"🎉 المعدل النهائي = {avg:.2f}")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.regex("|".join(list(subjects_flow.keys()) + ["📊 احسب المعدل"])), select_subject))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_value))

updater.start_polling()
updater.idle()

