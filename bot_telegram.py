import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from groq import Groq

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# Cliente de Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Almacenar conversaciones por usuario
conversaciones = {}

# Prompt del sistema
SYSTEM_PROMPT = """Eres un asistente experto en ingeniería que ayuda a estudiantes y profesionales.
Puedes ayudar con: Ingeniería Civil, Mecánica, Eléctrica, Industrial, Software, Matemáticas y Física aplicada.
Responde en español de forma clara, didáctica y profesional. Proporciona fórmulas, ejemplos y guía paso a paso cuando sea necesario."""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversaciones[user_id] = []
    await update.message.reply_text(
        "Hola! Soy tu asistente de ingeniería.\n"
        "Pregúntame lo que necesites sobre ingeniería, matemáticas o física.\n\n"
        "Comandos:\n"
        "/start - Reiniciar\n"
        "/clear - Limpiar conversación"
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    conversaciones[user_id] = []
    await update.message.reply_text("Conversación limpiada")


async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje_usuario = update.message.text

    # Inicializar si no existe
    if user_id not in conversaciones:
        conversaciones[user_id] = []

    # Agregar mensaje del usuario
    conversaciones[user_id].append({"role": "user", "content": mensaje_usuario})

    # Mantener solo últimos 20 mensajes
    if len(conversaciones[user_id]) > 20:
        conversaciones[user_id] = conversaciones[user_id][-20:]

    await update.message.chat.send_action("typing")

    try:
        # Llamada a Groq
        respuesta = groq_client.chat.completions.create(
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + conversaciones[user_id],
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            max_tokens=2048
        )

        texto_respuesta = respuesta.choices[0].message.content

        # Guardar respuesta en conversación
        conversaciones[user_id].append({"role": "assistant", "content": texto_respuesta})

        await update.message.reply_text(texto_respuesta)

    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("Bot iniciado...")
    app.run_polling()


if __name__ == '__main__':
    main()