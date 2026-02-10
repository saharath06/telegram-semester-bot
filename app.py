from telegram.ext import (
    Updater, CommandHandler, MessageHandler,
    Filters, ConversationHandler
)

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

ASK = 0  # حالة واحدة فقط (مهم)

QUESTIONS = [
    ("Vibration", "exam"),
    ("Vibration", "td"),
    ("Vibration", "tp"),

    ("Math", "exam"),
    ("Math", "td"),

    ("Electronic", "exam"),
    ("Electronic", "td"),
    ("Electronic", "tp"),

    ("Electrotechnic", "exam"),
    ("Electrotechnic", "td"),
    ("Electrotechnic", "tp"),

    ("Propability", "exam"),
    ("Propability", "td"),

    ("Informatique", "tp"),

    ("Energy", "exam"),
    ("Gene Electrice", "exam"),
    ("English", "exam"),
]

def start(update, context):
    context.user_data.clear()
    context.user_data["i"] = 0
    context.user_data["data"] = {}

    subject, part = QUESTIONS[0]
    update.message.reply_text(f"✏️ كم أخذت في {part.upper()} {subject}؟")
    return ASK

def ask(update, context):
    i = context.user_data.get("i", 0)

    # التحقق من الرقم
    try:
        value = float(update.message.text)
    except:
        update.message.reply_text("❌ أرسل رقم فقط")
        return ASK

    subject, part = QUESTIONS[i]
    context.user_data["data"].setdefault(subject, {})[part] = value

    i += 1
    context.user_data["i"] = i

    if i < len(QUESTIONS):
        subject, part = QUESTIONS[i]
        update.message.reply_text(f"✏️ كم أخذت في {part.upper()} {subject}؟")
        return ASK

    # ===== الحساب =====
    d = context.user_data["data"]

    def td_exam(td, ex):
        return 0.4 * td + 0.6 * ex

    grades = {
        "Vibration": td_exam(d["Vibration"]["td"], d["Vibration"]["exam"]),
        "Math": td_exam(d["Math"]["td"], d["Math"]["exam"]),
        "Electronic": td_exam(d["Electronic"]["td"], d["Electronic"]["exam"]),
        "Electrotechnic": td_exam(d["Electrotechnic"]["td"], d["Electrotechnic"]["exam"]),
        "Propability": td_exam(d["Propability"]["td"], d["Propability"]["exam"]),
        "Informatique": d["Informatique"]["tp"],
        "Energy": d["Energy"]["exam"],
        "Gene Electrice": d["Gene Electrice"]["exam"],
        "English": d["English"]["exam"],
        "TP_Vibration": d["Vibration"]["tp"],
        "TP_Elec_Electro": (d["Electronic"]["tp"] + d["Electrotechnic"]["tp"]) / 2,
    }

    CREDITS = {
        "Math": 6,
        "Vibration": 4,
        "Electronic": 4,
        "Electrotechnic": 4,
        "Propability": 4,
        "Informatique": 2,
        "TP_Elec_Electro": 2,
        "TP_Vibration": 1,
        "Energy": 1,
        "English": 1,
        "Gene Electrice": 1,
    }

    total, coef = 0, 0
    for m, c in CREDITS.items():
        total += grades[m] * c
        coef += c

    avg = total / coef

    report = f"📊 المعدل العام: {avg:.2f}\n\n"
    for m, v in grades.items():
        report += f"- {m}: {v:.2f}\n"

    update.message.reply_text(report)
    context.bot.send_message(chat_id=ADMIN_ID, text=report)

    return ConversationHandler.END


conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        ASK: [MessageHandler(Filters.text & ~Filters.command, ask)]
    },
    fallbacks=[CommandHandler("start", start)],
)

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(conv)

updater.start_polling()
updater.idle()
