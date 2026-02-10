from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

# تسلسل الأسئلة
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

# الكريدي
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

# المجموعات
GROUPS = {
    "G1": ["Gene Electrice", "Energy"],
    "G2": ["Math", "Vibration", "Electronic", "Electrotechnic"],
    "G3": ["Informatique", "TP_Vibration", "TP_Elec_Electro", "Propability"],
    "G4": ["English"],
}

users = {}

def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {"i": 0, "j": 0, "data": {}}
    subj, steps = FLOW[0]
    update.message.reply_text(f"✏️ كم أخذت في {steps[0].upper()} {subj}؟")

def handle(update, context):
    uid = update.message.from_user.id
    if uid not in users:
        update.message.reply_text("أرسل /start أولًا")
        return

    try:
        val = float(update.message.text)
    except:
        update.message.reply_text("❌ أرسل رقم فقط")
        return

    st = users[uid]
    subj, steps = FLOW[st["i"]]
    step = steps[st["j"]]

    st["data"].setdefault(subj, {})[step] = val
    st["j"] += 1

    if st["j"] < len(steps):
        update.message.reply_text(f"✏️ كم أخذت في {steps[st['j']].upper()} {subj}؟")
        return

    st["i"] += 1
    st["j"] = 0

    if st["i"] < len(FLOW):
        ns, ns_steps = FLOW[st["i"]]
        update.message.reply_text(f"✏️ كم أخذت في {ns_steps[0].upper()} {ns}؟")
        return

    d = st["data"]

    def td_exam(td, ex): return 0.4*td + 0.6*ex

    grades = {}
    grades["Vibration"] = td_exam(d["Vibration"]["td"], d["Vibration"]["exam"])
    grades["Math"] = td_exam(d["Math"]["td"], d["Math"]["exam"])
    grades["Electronic"] = td_exam(d["Electronic"]["td"], d["Electronic"]["exam"])
    grades["Electrotechnic"] = td_exam(d["Electrotechnic"]["td"], d["Electrotechnic"]["exam"])
    grades["Propability"] = td_exam(d["Propability"]["td"], d["Propability"]["exam"])
    grades["Energy"] = d["Energy"]["exam"]
    grades["English"] = d["English"]["exam"]
    grades["Gene Electrice"] = d["Gene Electrice"]["exam"]
    grades["Informatique"] = d["Informatique"]["tp"]
    grades["TP_Vibration"] = d["Vibration"]["tp"]
    grades["TP_Elec_Electro"] = (d["Electronic"]["tp"] + d["Electrotechnic"]["tp"]) / 2

    total, coef = 0, 0
    for k, v in grades.items():
        if k in CREDITS:
            total += v * CREDITS[k]
            coef += CREDITS[k]
    avg = total / coef

    group_avg = {}
    for g, mods in GROUPS.items():
        s = [grades[m] for m in mods if m in grades]
        group_avg[g] = sum(s)/len(s)

    earned = {}
    for m, c in CREDITS.items():
        if m in grades and grades[m] >= 10:
            earned[m] = c
        else:
            for g, mods in GROUPS.items():
                if m in mods and group_avg[g] >= 10:
                    earned[m] = c

    user = update.message.from_user
    header = f"👤 {user.first_name}\n📊 المعدل العام: {avg:.2f}\n\n"
    body = "📚 التفاصيل:\n"
    for m, v in grades.items():
        body += f"- {m}: {v:.2f}\n"
    body += "\n🎓 الكريدي المتحصل عليه:\n"
    for m, c in earned.items():
        body += f"- {m}: {c}\n"
    body += f"\n✅ مجموع الكريدي: {sum(earned.values())}"

    update.message.reply_text(header + body)
    context.bot.send_message(chat_id=ADMIN_ID, text=header + body)

    del users[uid]

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher
dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))
updater.start_polling()
updater.idle()
