from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

# المواد بالترتيب
SUBJECTS = [
    ("Vibration", ["exam", "td", "tp"]),
    ("Math", ["exam", "td"]),
    ("Electronic", ["exam", "td", "tp"]),
    ("Electrotechnic", ["exam", "td", "tp"]),
    ("Propability", ["exam", "td"]),
    ("Informatique", ["tp"]),
    ("Energy", ["exam"]),
    ("Gene Electrice", ["exam"]),
    ("English", ["exam"]),
]

users = {}

def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {
        "subject_index": 0,
        "step_index": 0,
        "data": {}
    }

    subject, steps = SUBJECTS[0]
    update.message.reply_text(f"✏️ كم أخذت في {steps[0].upper()} {subject}؟")

def handle(update, context):
    uid = update.message.from_user.id

    if uid not in users:
        update.message.reply_text("أرسل /start أولًا")
        return

    # التحقق من الرقم
    try:
        value = float(update.message.text)
    except:
        update.message.reply_text("❌ أرسل رقم فقط")
        return

    state = users[uid]

    subject, steps = SUBJECTS[state["subject_index"]]
    step = steps[state["step_index"]]

    # حفظ القيمة
    state["data"].setdefault(subject, {})[step] = value
    state["step_index"] += 1

    # نفس المادة
    if state["step_index"] < len(steps):
        next_step = steps[state["step_index"]]
        update.message.reply_text(f"✏️ كم أخذت في {next_step.upper()} {subject}؟")
        return

    # الانتقال لمادة جديدة
    state["subject_index"] += 1
    state["step_index"] = 0

    if state["subject_index"] < len(SUBJECTS):
        next_subject, next_steps = SUBJECTS[state["subject_index"]]
        update.message.reply_text(f"✏️ كم أخذت في {next_steps[0].upper()} {next_subject}؟")
        return

    # ===== الحساب =====
    d = state["data"]

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

    # معاملات
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

    # تقرير
    report = f"📊 المعدل العام: {avg:.2f}\n\n"
    for m, v in grades.items():
        report += f"- {m}: {v:.2f}\n"

    update.message.reply_text(report)
    context.bot.send_message(chat_id=ADMIN_ID, text=report)

    del users[uid]

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
updater.start_polling()
updater.idle()
