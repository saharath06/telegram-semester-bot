from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

# ====== تسلسل المواد (اسم واحد فقط في كل الملف) ======
FLOW = [
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

# ====== الكريدي ======
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

# ====== المجموعات ======
GROUPS = {
    "G1": ["Gene Electrice", "Energy"],
    "G2": ["Math", "Vibration", "Electronic", "Electrotechnic"],
    "G3": ["Informatique", "TP_Vibration", "TP_Elec_Electro", "Propability"],
    "G4": ["English"],
}

users = {}

# ====== /start ======
def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {"si": 0, "ti": 0, "data": {}}

    subject, steps = FLOW[0]
    update.message.reply_text(f"✏️ كم أخذت في {steps[0].upper()} {subject}؟")

# ====== استقبال الأرقام ======
def handle(update, context):
    uid = update.message.from_user.id

    if uid not in users:
        update.message.reply_text("أرسل /start أولًا")
        return

    try:
        value = float(update.message.text)
    except:
        update.message.reply_text("❌ أرسل رقم فقط")
        return

    state = users[uid]
    subject, steps = FLOW[state["si"]]
    step = steps[state["ti"]]

    # حفظ القيمة
    state["data"].setdefault(subject, {})[step] = value
    state["ti"] += 1

    # نفس المادة
    if state["ti"] < len(steps):
        next_step = steps[state["ti"]]
        update.message.reply_text(f"✏️ كم أخذت في {next_step.upper()} {subject}؟")
        return

    # مادة جديدة
    state["si"] += 1
    state["ti"] = 0

    if state["si"] < len(FLOW):
        next_subject, next_steps = FLOW[state["si"]]
        update.message.reply_text(f"✏️ كم أخذت في {next_steps[0].upper()} {next_subject}؟")
        return

    # ====== الحساب النهائي ======
    d = state["data"]

    def td_exam(td, ex):
        return 0.4 * td + 0.6 * ex

    grades = {}
    grades["Vibration"] = td_exam(d["Vibration"]["td"], d["Vibration"]["exam"])
    grades["Math"] = td_exam(d["Math"]["td"], d["Math"]["exam"])
    grades["Electronic"] = td_exam(d["Electronic"]["td"], d["Electronic"]["exam"])
    grades["Electrotechnic"] = td_exam(d["Electrotechnic"]["td"], d["Electrotechnic"]["exam"])
    grades["Propability"] = td_exam(d["Propability"]["td"], d["Propability"]["exam"])
    grades["Informatique"] = d["Informatique"]["tp"]
    grades["Energy"] = d["Energy"]["exam"]
    grades["Gene Electrice"] = d["Gene Electrice"]["exam"]
    grades["English"] = d["English"]["exam"]
    grades["TP_Vibration"] = d["Vibration"]["tp"]
    grades["TP_Elec_Electro"] = (d["Electronic"]["tp"] + d["Electrotechnic"]["tp"]) / 2

    # ====== المعدل العام ======
    total, coef = 0, 0
    for m, c in CREDITS.items():
        if m in grades:
            total += grades[m] * c
            coef += c

    avg = total / coef

    # ====== معدل المجموعات ======
    group_avg = {}
    for g, mods in GROUPS.items():
        vals = [grades[m] for m in mods if m in grades]
        group_avg[g] = sum(vals) / len(vals)

    # ====== حساب الكريدي ======
    earned = {}
    for m, c in CREDITS.items():
        if m in grades and grades[m] >= 10:
            earned[m] = c
        else:
            for g, mods in GROUPS.items():
                if m in mods and group_avg[g] >= 10:
                    earned[m] = c

    # ====== التقرير ======
    user = update.message.from_user
    report = (
        f"👤 {user.first_name}\n"
        f"🔗 @{user.username if user.username else '—'}\n"
        f"📊 المعدل العام: {avg:.2f}\n\n"
        f"📚 المواد:\n"
    )

    for m, v in grades.items():
        report += f"- {m}: {v:.2f}\n"

    report += "\n🎓 الكريدي:\n"
    for m, c in earned.items():
        report += f"- {m}: {c}\n"

    report += f"\n✅ مجموع الكريدي: {sum(earned.values())}"

    update.message.reply_text(report)
    context.bot.send_message(chat_id=ADMIN_ID, text=report)

    # تنظيف الجلسة
    del users[uid]

# ====== التشغيل ======
updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

updater.start_polling()
updater.idle()
