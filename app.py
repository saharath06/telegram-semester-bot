from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

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

users = {}

def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {"i": 0, "data": {}}
    subject, part = QUESTIONS[0]
    update.message.reply_text(f"✏️ كم أخذت في {part.upper()} {subject}؟")

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
    i = state["i"]

    if i >= len(QUESTIONS):
        update.message.reply_text("أرسل /start من جديد")
        return

    subject, part = QUESTIONS[i]
    state["data"].setdefault(subject, {})[part] = value
    state["i"] += 1

    # سؤال التالي
    if state["i"] < len(QUESTIONS):
        ns, np = QUESTIONS[state["i"]]
        update.message.reply_text(f"✏️ كم أخذت في {np.upper()} {ns}؟")
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

    GROUPS = {
        "G1": ["Gene Electrice", "Energy"],
        "G2": ["Math", "Vibration", "Electronic", "Electrotechnic"],
        "G3": ["Informatique", "TP_Vibration", "TP_Elec_Electro", "Propability"],
        "G4": ["English"],
    }

    total, coef = 0, 0
    for m, c in CREDITS.items():
        total += grades[m] * c
        coef += c
    avg = total / coef

    group_avg = {}
    for g, mods in GROUPS.items():
        group_avg[g] = sum(grades[m] for m in mods) / len(mods)

    earned = {}
    for m, c in CREDITS.items():
        if grades[m] >= 10:
            earned[m] = c
        else:
            for g, mods in GROUPS.items():
                if m in mods and group_avg[g] >= 10:
                    earned[m] = c

    total_credits = sum(earned.values())

    user = update.message.from_user
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    username = f"@{user.username}" if user.username else "لا يوجد"

    report = (
        f"👤 الاسم: {name}\n"
        f"🔗 المستخدم: {username}\n"
        f"📊 المعدل العام: {avg:.2f}\n\n"
    )

    for m, v in grades.items():
        report += f"- {m}: {v:.2f}\n"

    report += "\n🎓 الكريدي:\n"
    for m, c in earned.items():
        report += f"- {m}: {c}\n"

    report += f"\n✅ مجموع الكريدي: {total_credits}"

    update.message.reply_text(report)
    context.bot.send_message(chat_id=ADMIN_ID, text=report)

    del users[uid]  # تنظيف الجلسة

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

updater.start_polling(drop_pending_updates=True)
updater.idle()
