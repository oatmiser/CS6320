from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN:Final = ""
USERNAME:Final = "CometFoodBot"
state = ""

# Commands
async def start_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello, I can't do anything yet!")
async def help_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please type something so I can respond.")
async def custom_command(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is the custom command")

# Give info to Food bot
async def beginPlan(update:Update, context:ContextTypes.DEFAULT_TYPE):
    global state
    state = "define_plan"
    await update.message.reply_text("Would you like to name this plan?")
async def endPlan(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    global state
    state = ""
    await update.message.reply_text(f"Plan {plan} is created! Use /{plan} whenever you want to see it again.")
async def forgetPlan(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    global state
    state = "forget_plan"
    await update.message.reply_text(f"Are you sure that I should forget Plan {plan}? This action cannot be undone.")

async def showIngredients(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} uses ingredients:\nx\ny\nz")
async def showBudget(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} was generated with a budget of X")
async def showGoal(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} has no goal specified")
async def costOf(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} has a total cost of A")
async def nutritionOf(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} as targets good nutrition for: c,d,e,f")
async def update(update:Update, context:ContextTypes.DEFAULT_TYPE, plan, key, value):
    await update.message.reply_text(f"{key} of Plan {plan} was changed to {value}")
async def info(update:Update, context:ContextTypes.DEFAULT_TYPE, ingredient):
    await update.message.reply_text(f"{ingredient} is bobloblaw")
async def generateSimilar(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    await update.message.reply_text(f"Plan {plan} is related to Plan new")



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
    print(f"({update.message.chat.id}) Received {message_type} chat: <{text}>")

    if message_type=='supergroup':
        if USERNAME in text:
            new_text:str = text.replace(USERNAME,'').strip()
            response:str = handle_response(new_text)
        else:
            # no response if the chat is not mentioning @bot
            return
    else:
        response:str = handle_response(text)
    
    print("\tBot:", response, "\n")
    await update.message.reply_text(response)

async def error(update:Update, context:ContextTypes.DEFAULT_TYPE):
    print(f"Update {update} caused error {context.error}")

if __name__ == "__main__":
    print("Starting")
    app = Application.builder().token(TOKEN).read_timeout(30).write_timeout(30).build()

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
