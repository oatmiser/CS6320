from typing import Final
# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# https://www.youtube.com/watch?v=vZtm1wuA2yc
TOKEN:Final = "nxp210016 's secret"
USERNAME:Final = "CometFoodBot"

# Commands
async def start_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I can't do anything yet!")

async def help_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type something so I can respond.")

async def custom_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is the custom command")


# Responses
def handle_response(text:str) -> str:
    processed:str = text.lower()

    if "hello" in processed:
        return "Welcome to myself"
    return "I DON'T UNDERSTAND YOU"

async def handle_message(update:Update, context:ContextTypes.DEFAULT_TYPE):
    message_type:str = update.message.chat.type # group or private chat
    text:str = update.message.text # user message to process
    # log all incoming
    print(f"{update.message.chat.id} in {message_type}: '{text}")

    if message_type=='group':
        if USERNAME in text:
            new_text:str = text.replace(USERNAME,'').strip()
            response:str = handle_response(new_text)
        else:
            # no response if the chat is not mentioning @bot
            return
    else:
        response:str = handle_response(text)
    
    print("Bot:", response)
    await update.message.reply_text(response)

async def error(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("Starting")
    app = Application.builder().token(TOKEN).build()

    # Commands (not with arguments)
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Errors
    app.add_error_handler(error)

    # Check for new messages (seconds)
    print("Polling")
    app.run_polling(poll_interval=3)
