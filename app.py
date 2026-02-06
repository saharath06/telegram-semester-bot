from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

user_data = {}
current_subject = {}

subjects = [
    "Vibration", "Math 3", "Electronic", "Electrotechnic",
    "Energy", "Propability", "English", "Cinétique", "Informatique"
]

def start(update, context):
    uid = update.message.from_user.id
    user_data[uid] = {}
    current_subject[uid] = None

    keyboard = [
        ["Vibration", "Math 3"],
        ["Electronic", "Electrotechnic"],
        ["Energy", "Propability"],
        ["English", "Cinétique"],
        ["Informatique"],
        ["📊 احسب المعدل"]
    ]

    update.message.reply_text(
        "👋 أهلاً\nاختر المادة وأدخل النقاط:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

def select_subject(update, context):
    uid = update.message.from_user.id
    text = update.message.text

    if text == "📊 احسب المعدل":
        calculate(update, context)
        return

    current_subject[uid] = text
    update.message.reply_text(
        "✏️ أدخل النقاط:\n"
        "- Exam فقط: exam\n"
        "- TD + Exam: TD Exam\n"
        "- TP TD Exam: TP TD Exam"
    )

def save_grades(update, context):
    uid = update.message.from_user.id
    sub = current_subject.get(uid)
    if not sub:
        return

    values = list(map(float, update.message.text.split()))
    d = {}

    if sub in ["Energy", "English", "Cinétique"]:
        d["exam"] = values[0]

    elif sub in ["Math 3", "Propability"]:
        d["td"], d["exam"] = values

    elif sub == "Informatique":
        d["tp"] = values[0]

    else:
        d["tp"], d["td"], d["exam"] = values

    user_data[uid][sub] = d
    update.message.reply_text("✅ تم الحفظ")

def calculate(update, context):
    uid = update.message.from_user.id
    data = user_data.get(uid, {})

    def td_exam(td, ex): return 0.4*td + 0.6*ex

    total = 0
    coef = 0

    total += td_exam(data["Math 3"]["td"], data["Math 3"]["exam"]) * 3; coef += 3
    total += td_exam(data["Vibration"]["td"], data["Vibration"]["exam"]) * 2; coef += 2
    total += td_exam(data["Electronic"]["td"], data["Electronic"]["exam"]) * 2; coef += 2
    total += td_exam(data["Electrotechnic"]["td"], data["Electrotechnic"]["exam"]) * 2; coef += 2
    total += td_exam(data["Propability"]["td"], data["Propability"]["exam"]) * 2; coef += 2

    total += data["Energy"]["exam"]; coef += 1
    total += data["English"]["exam"]; coef += 1
    total += data["Cinétique"]["exam"]; coef += 1

    total += data["Informatique"]["tp"]; coef += 1
    total += data["Vibration"]["tp"]; coef += 1
    total += (data["Electronic"]["tp"] + data["Electrotechnic"]["tp"]) / 2; coef += 1

    avg = total / coef

    user = update.message.from_user
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "لا يوجد"

    report = f"📩 نتيجة حساب سداسي\n\n👤 الاسم: {name}\n🔗 المستخدم: {username}\n\n"
    for s in subjects:
        report += f"- {s}: {data.get(s)}\n"
    report += f"\n📊 المعدل العام = {avg:.2f}"

    context.bot.send_message(chat_id=ADMIN_ID, text=report)
    update.message.reply_text(f"🎉 المعدل النهائي = {avg:.2f}\n📨 تم إرسال التفاصيل للإدارة")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex("|".join(subjects + ["📊 احسب المعدل"])), select_subject))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_grades))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
