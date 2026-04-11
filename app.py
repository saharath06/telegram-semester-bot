from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI

client = OpenAI(
    api_key="sk-Nm3CRnIJjnHgBc8U9lHgN6ZSGU7UXPh3ROLrlPbAvy6N77AS",
    base_url="https://api.souimagery.fun/v1"
)

SYSTEM_PROMPT = "أنا المساعد الذكي لصحارة ثامر، تمت برمجتي من قبل صحارة ثامر لمساعدتك."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    response = client.chat.completions.create(
        model="gpt-5.4",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    )

    reply = response.choices[0].message.content
    await update.message.reply_text(reply)

app = ApplicationBuilder().token("8581934344:AAHkfcRnePypV_NQlvyctAasXnjS7v6io-k").build()
app.add_handler(MessageHandler(filters.TEXT, handle_message))

app.run_polling()
