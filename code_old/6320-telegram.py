from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

#from chatbot import UserPlan
#from chatbot import add_plan
class UserPlan:
    def __init__(self, name:str, budget:float = 0, goal:str = "None", ingredients:list = [], time:int = 0):
        self.name = name
        self.budget = budget
        self.goal = goal
        self.ingredients = ingredients
        self.time = time

    def display(self) -> str:
        str_build = f"Plan {self.name}:\n"
        for attr in dir(self):
            if not callable(getattr(self, attr)) and not attr.startswith("__"):
                str_build += f"\t{attr} {getattr(self, attr)}\n"
        return str_build

    def set_name(self, name:str):
        self.name = name
    def set_budget(self, amount:float):
        self.budget = amount
    def set_time(self, amount:int):
        self.time = amount
    def set_goal(self, desc:str):
        self.goal = desc
    def set_ingredients(self, food:list):
        self.ingredients = food

user_plans = dict()
def add_plan(name:str, budget:float, goal:str, ingredients:list, time:int):
    global user_plans
    user_plans[name] = UserPlan(name, budget, goal, ingredients, time)


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

# stuff
async def new_plan(update:Update, context:ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("what am i doing...")


# Give info to Food bot
async def begin_plan(update:Update, context:ContextTypes.DEFAULT_TYPE):
    global state
    state = "define_plan"
    await update.message.reply_text("Would you like to name this plan?")
async def end_plan(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
    global state
    state = ""
    await update.message.reply_text(f"Plan {plan} is created! Use /{plan} whenever you want to see it again.")
async def forget_plan(update:Update, context:ContextTypes.DEFAULT_TYPE, plan):
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
    global user_plans
    processed:str = text.split(" ")[0].lower()
    rest = " ".join(text.split(" ")[1:]).lower()

    reply_text = "temp"
    match processed:
        case "hello":
            reply_text = "Welcome to CometFoodBot"

        case "new":
            split = rest.split(" ")
            name = split[0]
            time = int(split[1])
            budget = float(split[2])
            ingredient_list = split[3].split(",") # csv
            goal = " ".join(split[4:])

            add_plan(name, budget, goal, ingredient_list, time)

            reply_text = f"{name} has been added to your Food Plans!\nYou can view it using 'show {name}'"

        case "edit":
            split = rest.split(" ")
            plan_name = split[0]
            update_var = split[1]
            if plan_name in user_plans:
                user_plans[plan_name].display()
                # use <state> var to get a new input from user??
                match update_var:
                    case "budget":
                        user_plans[plan_name].set_budget(float(split[2]))
                        reply_text = f"Budget for {plan_name} was updated"
                    case "goal":
                        user_plans[plan_name].set_goal(" ".join(split[2:]))
                        reply_text = f"User goal for {plan_name} was updated"
                    case "ingredients":
                        user_plans[plan_name].set_ingredients(" ".join(split[2:]).split(","))
                        reply_text = f"Ingredients available for {plan_name} were updated"
                    case "time":
                        user_plans[plan_name].set_time(int(split[2]))
                        reply_text = f"Prep time was updated for {plan_name}"
                    case _:
                        reply_text = f"Sorry, this value doesn't exist or cannot be changed."
            else:
                reply_text = "Sorry, this plan does not exist!"

        case "forget":
            plan_name = rest
            if plan_name in user_plans:
                # TODO wait for user confirmation in another message
                user_plans.pop(plan_name)
                reply_text = f"{plan_name} was removed from your Food Plans."
            else:
                reply_text = "Sorry, this plan does not exist!"

        case "show":
            plan_name = rest
            if plan_name in user_plans:
                reply_text = user_plans[plan_name].display()
            else:
                reply_text = "Sorry, this plan does not exist!"

        case "recommend":
            reply_text = "Sorry, that function is currently unavailable"

        case _:
            reply_text = "Sorry, I can't understand your message."

    return reply_text

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
    app.add_handler(CommandHandler("new", new_plan))
    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    # Errors
    app.add_error_handler(error)

    # Check for new messages (seconds)
    print("Polling")
    app.run_polling(poll_interval=3)
