from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"

# ترتيب المواد والخطوات
FLOW = [
    ("Vibration", ["exam", "td", "tp"], 2),
    ("Math 3", ["exam", "td"], 3),
    ("Electronic", ["exam", "td", "tp"], 2),
    ("Electrotechnic", ["exam", "td", "tp"], 2),
    ("Propability", ["exam", "td"], 2),
    ("Energy", ["exam"], 1),
    ("English", ["exam"], 1),
    ("Cinétique", ["exam"], 1),
    ("Informatique", ["tp"], 1),
]

users = {}

def start(update, context):
    uid = update.message.from_user.id
    users[uid] = {
        "subject_i": 0,
        "step_i": 0,
        "data": {}
    }
    subject, steps, _ = FLOW[0]
    update.message.reply_text(f"✏️ ارسلي {steps[0].upper()} {subject}")

def handle(update, context):
    uid = update.message.from_user.id
    if uid not in users:
        update.message.reply_text("ارسلي /start أولًا")
        return

    try:
        value = float(update.message.text)
    except:
        update.message.reply_text("❌ ارسلي رقم فقط")
        return

    state = users[uid]
    subject, steps, coef = FLOW[state["subject_i"]]
    step = steps[state["step_i"]]

    state["data"].setdefault(subject, {})[step] = value
    state["step_i"] += 1

    # نفس المادة
    if state["step_i"] < len(steps):
        next_step = steps[state["step_i"]]
        update.message.reply_text(f"✏️ ارسلي {next_step.upper()} {subject}")
        return

    # مادة جديدة
    state["subject_i"] += 1
    state["step_i"] = 0

    if state["subject_i"] < len(FLOW):
        subject, steps, _ = FLOW[state["subject_i"]]
        update.message.reply_text(f"✏️ ارسلي {steps[0].upper()} {subject}")
        return

    # الحساب النهائي
    total, coef_sum = 0, 0

    def td_exam(td, ex):
        return 0.4 * td + 0.6 * ex

    d = state["data"]

    total += td_exam(d["Vibration"]["td"], d["Vibration"]["exam"]) * 2; coef_sum += 2
    total += td_exam(d["Math 3"]["td"], d["Math 3"]["exam"]) * 3; coef_sum += 3
    total += td_exam(d["Electronic"]["td"], d["Electronic"]["exam"]) * 2; coef_sum += 2
    total += td_exam(d["Electrotechnic"]["td"], d["Electrotechnic"]["exam"]) * 2; coef_sum += 2
    total += td_exam(d["Propability"]["td"], d["Propability"]["exam"]) * 2; coef_sum += 2

    total += d["Energy"]["exam"]; coef_sum += 1
    total += d["English"]["exam"]; coef_sum += 1
    total += d["Cinétique"]["exam"]; coef_sum += 1

    total += d["Informatique"]["tp"]; coef_sum += 1
    total += d["Vibration"]["tp"]; coef_sum += 1
    total += (d["Electronic"]["tp"] + d["Electrotechnic"]["tp"]) / 2; coef_sum += 1

    avg = total / coef_sum

    ADMIN_ID = 7623960185

report = (
    f"👤 الاسم: {update.message.from_user.first_name}\n"
    f"🔗 اليوزر: @{update.message.from_user.username}\n"
    f"📊 المعدل: {avg:.2f}\n"
    f"🧾 التفاصيل:\n{state['data']}"
)

context.bot.send_message(chat_id=ADMIN_ID, text=report)

    update.message.reply_text(f"📊 معدلك = {avg:.2f}")

    if avg < 10:
        update.message.reply_text("نتلاقو في الراطراباج")
    else:
        update.message.reply_text("😎 بصحتك شلقمني لحسد")

    del users[uid]  # تنظيف الذاكرة

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle))

updater.start_polling()
updater.idle()
