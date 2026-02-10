from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

TOKEN = "7451840667:AAFsqAuuzzdAjlBit9vHKCrPx64k9Ghz_8U"
ADMIN_ID = 7623960185

def start(update, context):
    update.message.reply_text(
        "✏️ أرسل النقاط بهذا الشكل (سطر لكل مادة):\n\n"
        "Vibration_exam Vibration_td Vibration_tp\n"
        "Math_exam Math_td\n"
        "Electronic_exam Electronic_td Electronic_tp\n"
        "Electrotechnic_exam Electrotechnic_td Electrotechnic_tp\n"
        "Propability_exam Propability_td\n"
        "Informatique_tp\n"
        "Energy_exam\n"
        "GeneElectrice_exam\n"
        "English_exam\n\n"
        "📌 مثال:\n"
        "12 10 14\n"
        "11 9\n"
        "10 8 12\n"
        "11 9 10\n"
        "14 12\n"
        "15\n"
        "13\n"
        "14\n"
        "16"
    )

def calculate(update, context):
    try:
        lines = update.message.text.strip().split("\n")

        def td_exam(td, ex):
            return 0.4 * td + 0.6 * ex

        grades = {}
        grades["Vibration"] = td_exam(float(lines[0].split()[1]), float(lines[0].split()[0]))
        tp_vibration = float(lines[0].split()[2])

        grades["Math"] = td_exam(float(lines[1].split()[1]), float(lines[1].split()[0]))

        grades["Electronic"] = td_exam(float(lines[2].split()[1]), float(lines[2].split()[0]))
        tp_elec = float(lines[2].split()[2])

        grades["Electrotechnic"] = td_exam(float(lines[3].split()[1]), float(lines[3].split()[0]))
        tp_electro = float(lines[3].split()[2])

        grades["Propability"] = td_exam(float(lines[4].split()[1]), float(lines[4].split()[0]))

        grades["Informatique"] = float(lines[5])
        grades["Energy"] = float(lines[6])
        grades["Gene Electrice"] = float(lines[7])
        grades["English"] = float(lines[8])

        grades["TP_Vibration"] = tp_vibration
        grades["TP_Elec_Electro"] = (tp_elec + tp_electro) / 2

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
        full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        username = f"@{user.username}" if user.username else "لا يوجد"

        report = (
            f"👤 الاسم: {full_name}\n"
            f"🔗 المستخدم: {username}\n"
            f"📊 المعدل العام: {avg:.2f}\n\n"
            f"📚 المواد:\n"
        )

        for m, v in grades.items():
            report += f"- {m}: {v:.2f}\n"

        report += "\n🎓 الكريدي:\n"
        for m, c in earned.items():
            report += f"- {m}: {c}\n"

        report += f"\n✅ مجموع الكريدي: {total_credits}"

        update.message.reply_text(report)
        context.bot.send_message(chat_id=ADMIN_ID, text=report)

    except Exception as e:
        update.message.reply_text("❌ خطأ في الإدخال، تأكد من الشكل وعدد الأسطر")

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(Filters.text & ~Filters.command, calculate))

updater.start_polling(drop_pending_updates=True)
updater.idle()
