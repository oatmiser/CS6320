from typing import Final
import spacy
import re
from datetime import datetime
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from config import SPOONACULAR_API_KEY, TELETOKEN

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")

class ConversationState:
    def __init__(self):
        self.current_state = None
        self.pending_fields = {}
        self.collected_data = {}
        self.current_plan_name = None
        self.last_activity = datetime.now()

class UserPlan:
    _recipe_cache = {}  # Class-level cache for recipe details
    
    def __init__(self, name: str, budget: float = 0, goal: str = "None", ingredients: list = None, time: int = 0):
        if not name:
            raise ValueError("Name cannot be empty")
        if budget < 0:
            raise ValueError("Budget must be positive")
        if time < 0:
            raise ValueError("Time must be positive")
        self.name = name
        self.budget = budget
        self.goal = goal
        self.ingredients = ingredients or []
        self.time = time
        self.recipes = []

    def fetch_recipes(self) -> None:
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'ingredients': ','.join(self.ingredients),
            'maxReadyTime': self.time,
            'maxPrice': self.budget,
            'number': 5,
            'ranking': 2,
            'ignorePantry': True
        }
        
        if self.goal.lower() != 'none':
            params['diet'] = self.goal.lower()
            
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(
                    'https://api.spoonacular.com/recipes/findByIngredients',
                    params=params,
                    timeout=(5, 15)  # Connect timeout, Read timeout
                )
                response.raise_for_status()
                recipes = response.json()
                self.recipes = self.filter_recipes(recipes)
                break
            except requests.Timeout:
                if attempt == max_retries - 1:
                    raise TimeoutError("Recipe search timed out after multiple attempts")
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.RequestException as e:
                self.recipes = []
                raise Exception(f"API Error: {str(e)}")

    def filter_recipes(self, recipes: list) -> list:
        filtered = []
        seen_recipes = set()
        
        for recipe in recipes:
            if recipe['id'] in seen_recipes:
                continue
                
            recipe_details = self.fetch_recipe_details(recipe['id'])
            if recipe_details and self._meets_criteria(recipe_details):
                filtered.append(recipe_details)
                seen_recipes.add(recipe['id'])
                
            if len(filtered) >= 5:  # Limit number of recipes
                break
        return filtered

    def _meets_criteria(self, recipe: dict) -> bool:
        return (recipe['readyInMinutes'] <= self.time and
                recipe['pricePerServing']/100 <= self.budget and
                self.check_nutrition_goals(recipe))

    def check_nutrition_goals(self, recipe: dict) -> bool:
        if self.goal.lower() == 'none':
            return True
            
        nutrition = recipe.get('nutrition', {}).get('nutrients', [])
        goal_checks = {
            'low_carb': lambda n: next((x['amount'] for x in n if x['name'] == 'Carbohydrates'), 0) < 50,
            'high_protein': lambda n: next((x['amount'] for x in n if x['name'] == 'Protein'), 0) > 25,
            'low_fat': lambda n: next((x['amount'] for x in n if x['name'] == 'Fat'), 0) < 15,
            'low_calorie': lambda n: next((x['amount'] for x in n if x['name'] == 'Calories'), 0) < 500,
            'keto': lambda n: (next((x['amount'] for x in n if x['name'] == 'Carbohydrates'), 0) < 20 and
                             next((x['amount'] for x in n if x['name'] == 'Fat'), 0) > 40)
        }
        
        return goal_checks.get(self.goal.lower(), lambda x: True)(nutrition)
    
    @classmethod
    def from_entities(cls, entities: dict, name: str):
        return cls(
            name=name,
            budget=entities.get('money', [0])[0],
            time=entities.get('time', [0])[0],
            ingredients=entities.get('ingredients', []),
            goal=entities.get('goal', 'None')
        )



    @classmethod
    def fetch_recipe_details(cls, recipe_id: int) -> dict:
        if recipe_id in cls._recipe_cache:
            return cls._recipe_cache[recipe_id]
            
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'includeNutrition': True
        }
        try:
            response = requests.get(
                f'https://api.spoonacular.com/recipes/{recipe_id}/information',
                params=params,
                timeout=(5, 15)
            )
            response.raise_for_status()
            recipe = response.json()
            cls._recipe_cache[recipe_id] = recipe
            return recipe
        except Exception as e:
            print(f"Error fetching recipe details: {str(e)}")
            return None

    def set_budget(self, amount: float):
        if amount < 0:
            raise ValueError("Budget must be positive")
        self.budget = amount

    def set_time(self, minutes: int):
        if minutes < 0:
            raise ValueError("Time must be positive")
        self.time = minutes

    def set_goal(self, goal: str):
        self.goal = goal

    def set_ingredients(self, ingredients: list):
        if not ingredients:
            raise ValueError("Ingredients list cannot be empty")
        self.ingredients = ingredients

    def display(self) -> str:
        str_build = f"Plan {self.name}:\n"
        for attr in ['budget', 'goal', 'ingredients', 'time']:
            str_build += f"\t{attr}: {getattr(self, attr)}\n"
        if self.recipes:
            str_build += "\tRecipes:\n"
            for recipe in self.recipes:
                str_build += f"\t- {recipe['title']}\n"
        return str_build

def format_recipe_details(recipe: dict) -> str:
    if not recipe:
        return "No recipe details available."

    nutrition = recipe.get('nutrition', {}).get('nutrients', [])
    calories = next((n['amount'] for n in nutrition if n['name'] == 'Calories'), 'N/A')
    protein = next((n['amount'] for n in nutrition if n['name'] == 'Protein'), 'N/A')
    carbs = next((n['amount'] for n in nutrition if n['name'] == 'Carbohydrates'), 'N/A')
    fat = next((n['amount'] for n in nutrition if n['name'] == 'Fat'), 'N/A')
    
    response = f"""🍽️ *{recipe.get('title', 'N/A')}*
⏰ Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes
👥 Servings: {recipe.get('servings', 'N/A')}
💰 Price per serving: ${recipe.get('pricePerServing', 0)/100:.2f}
🔥 Calories: {calories}
💪 Protein: {protein}g
🍞 Carbs: {carbs}g
🥑 Fat: {fat}g
📝 *Ingredients:*"""

    for ingredient in recipe.get('extendedIngredients', []):
        response += f"\n• {ingredient.get('original', 'N/A')}"
    
    if recipe.get('instructions'):
        response += f"\n\n👩‍🍳 *Instructions:*\n{recipe['instructions']}"
    
    return response

def fetch_recipe_details(recipe_id: int) -> dict:
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'includeNutrition': True
    }
    try:
        response = requests.get(
            f'https://api.spoonacular.com/recipes/{recipe_id}/information',
            params=params,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching recipe details: {str(e)}")
        return None

user_plans = dict()

def add_plan(name: str, budget: float, goal: str, ingredients: list, time: int):
    if not name or not ingredients:
        raise ValueError("Name and ingredients are required")
    if budget < 0 or time < 0:
        raise ValueError("Budget and time must be positive")
    user_plans[name] = UserPlan(name, budget, goal, ingredients, time)

TOKEN:Final = TELETOKEN
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
def handle_response(text: str) -> str:
    global user_plans
    if not text.strip():
        return "Please enter a command. Type 'help' for available commands."
    
    processed = text.split(" ")[0].lower()
    rest = " ".join(text.split(" ")[1:]).lower()

    match processed:
        case "hello" | "hi" | "start":
            return """
🎉 Welcome to CometFoodBot! 
I'm here to help you plan your meals and achieve your food goals.
Type 'help' to see what I can do for you!
"""

        case "new":
            try:
                split = rest.split(" ")
                if len(split) < 5:
                    return """
❌ Incorrect format! Please use:
'new <name> <time_minutes> <budget> <ingredients> <goal>'
Example: new HealthyMeal 30 20.50 chicken,rice,beans healthy eating
"""
                name = split[0]
                if name in user_plans:
                    return f"❌ A plan named '{name}' already exists. Choose a different name or edit the existing plan."
                
                time = int(split[1])
                budget = float(split[2])
                ingredient_list = [i.strip() for i in split[3].split(",")]
                goal = " ".join(split[4:])

                add_plan(name, budget, goal, ingredient_list, time)
                
                return f"""
✅ Successfully created plan: {name}
⏰ Time: {time} minutes
💰 Budget: ${budget:.2f}
🥗 Ingredients: {', '.join(ingredient_list)}
🎯 Goal: {goal}

Type 'show {name}' to view details
"""
            except (ValueError, IndexError):
                return "❌ Invalid input format. Type 'help' to see the correct format."

        case "edit":
            try:
                split = rest.split(" ")
                if len(split) < 3:
                    return "❌ Please specify what to edit: 'edit <plan_name> <budget/goal/ingredients/time> <new_value>'"
                
                plan_name = split[0]
                update_var = split[1]
                
                if plan_name not in user_plans:
                    return f"❌ Plan '{plan_name}' not found. Use 'show all' to see available plans."

                match update_var:
                    case "budget":
                        new_budget = float(split[2])
                        user_plans[plan_name].set_budget(new_budget)
                        return f"✅ Budget updated to ${new_budget:.2f}"
                    case "goal":
                        new_goal = " ".join(split[2:])
                        user_plans[plan_name].set_goal(new_goal)
                        return f"✅ Goal updated to: {new_goal}"
                    case "ingredients":
                        new_ingredients = [i.strip() for i in " ".join(split[2:]).split(",")]
                        user_plans[plan_name].set_ingredients(new_ingredients)
                        return f"✅ Ingredients updated to: {', '.join(new_ingredients)}"
                    case "time":
                        new_time = int(split[2])
                        user_plans[plan_name].set_time(new_time)
                        return f"✅ Prep time updated to {new_time} minutes"
                    case _:
                        return "❌ Invalid field. You can edit: budget, goal, ingredients, or time"
            except (ValueError, IndexError):
                return "❌ Invalid input format. Type 'help' to see the correct format."

        case "show":
            if not rest:
                return "❌ Please specify a plan name or use 'show all'"
            if rest == "all":
                if not user_plans:
                    return "No plans created yet. Use 'new' to create one!"
                return "\n\n".join([f"📋 Plan: {name}\n{plan.display()}" 
                                  for name, plan in user_plans.items()])
            if rest not in user_plans:
                return f"❌ Plan '{rest}' not found. Use 'show all' to see available plans."
            return user_plans[rest].display()

        case "forget":
            if not rest:
                return "❌ Please specify which plan to delete"
            if rest not in user_plans:
                return f"❌ Plan '{rest}' not found. Use 'show all' to see available plans."
            user_plans.pop(rest)
            return f"✅ Plan '{rest}' has been deleted"

        case "recommend":
            try:
                plan_name = rest
                if not plan_name:
                    return "❌ Please specify a plan name: 'recommend <plan_name>'"
                
                if plan_name not in user_plans:
                    return "❌ Plan not found. Use 'new' to create one first."
                
                plan = user_plans[plan_name]
                plan.fetch_recipes()
                
                if not plan.recipes:
                    return "No recipes found for your ingredients."
                
                response = f"🍽️ Recommended recipes for {plan_name}:\n\n"
                for idx, recipe in enumerate(plan.recipes[:3], 1):
                    recipe_details = fetch_recipe_details(recipe['id'])
                    if recipe_details:
                        response += format_recipe_details(recipe_details) + "\n\n"
                
                return response
            except Exception as e:
                return f"❌ Error: {str(e)}"

        case "help":
            return """
🤖 *CometFoodBot Commands*

📝 *Create & Manage Plans*
• /new <name> <time> <budget> <ingredients> <goal>

  Example: new lunch 60 15.50 chicken,rice,vegetables low_carb
  
⚡ *Available Health Goals:*
• low_carb - Less than 50g carbs per serving
• high_protein - More than 25g protein per serving
• low_fat - Less than 15g fat per serving
• low_calorie - Under 500 calories per serving
• keto - Less than 20g carbs and over 40g fat

🛠️ *Plan Management*
• /edit <plan> <field> <value>
  Fields:
  - budget (in dollars)
  - time (in minutes)
  - goal (health goals listed above)
  - ingredients (comma-separated)
• /show <plan> - View specific plan details
• /show all - View all your plans
• /forget <plan> - Delete a plan

🔍 *Recipe Commands*
• /recommend <plan> - Get personalized recipe suggestions based on your plan

💡 *Usage Tips*
• Time: Specify cooking time in minutes (e.g., 30, 45, 60)
• Budget: Enter amount in dollars (e.g., 15.50, 20.00)
• Ingredients: Separate with commas (e.g., chicken,rice,broccoli)
• Multiple words: Use underscores (e.g., ground_beef, olive_oil)

⚠️ *Constraints*
• Maximum cooking time: 120 minutes
• Minimum budget: $5.00
• Maximum ingredients: 10 items
"""
        
        case _:
            return "❌ Unknown command. Type 'help' to see available commands."

def format_recipe_details(recipe: dict) -> str:
    if not recipe:
        return "No recipe details available."
    
    response = f"""🍽️ *{recipe.get('title', 'N/A')}*
⏰ Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes
👥 Servings: {recipe.get('servings', 'N/A')}
💰 Price per serving: ${recipe.get('pricePerServing', 0)/100:.2f}

📝 *Ingredients:*"""
    
    for ingredient in recipe.get('extendedIngredients', []):
        response += f"\n• {ingredient.get('original', 'N/A')}"
    
    return response

def fetch_recipe_details(recipe_id: int) -> dict:
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'includeNutrition': True
    }
    try:
        response = requests.get(
            f'https://api.spoonacular.com/recipes/{recipe_id}/information',
            params=params
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching recipe details: {str(e)}")
        return None

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


def extract_entities(text: str) -> dict:
    doc = nlp(text)
    entities = {
        'time': [],
        'money': [],
        'ingredients': [],
        'goal': None,
        'command_type': None
    }
    
    # Detect command type
    command_patterns = {
    'new_plan': r'(want|need|create|make).*(meal|food|plan|diet)|create.*(?:low-carb|high-protein|keto)',
    'show_plan': r'(show|display|view|see).*plan',
    'edit_plan': r'(edit|modify|change|update).*plan'
    }
    
    text_lower = text.lower()
    for cmd_type, pattern in command_patterns.items():
        if re.search(pattern, text_lower):
            entities['command_type'] = cmd_type
            break

    # Enhanced time patterns
    time_patterns = [
        r'(\d+)\s*(minutes?|mins?|hours?|hrs?)',
        r'have\s*(\d+)\s*(minutes?|mins?|hours?|hrs?)',
        r'takes?\s*(\d+)\s*(minutes?|mins?|hours?|hrs?)',
        r'spend\s*(\d+)\s*(minutes?|mins?|hours?|hrs?)'
    ]
    
    # Enhanced money patterns
    money_patterns = [
        r'\$?\s*(\d+(?:\.\d{2})?)',
        r'budget.*?(\d+(?:\.\d{2})?)',
        r'costs?.*?\$?\s*(\d+(?:\.\d{2})?)',
        r'spend.*?\$?\s*(\d+(?:\.\d{2})?)'
    ]
    
    # Process time patterns
    for pattern in time_patterns:
        time_matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in time_matches:
            value = int(match.group(1))
            unit = match.group(2) if len(match.groups()) > 1 else 'minutes'
            if 'hour' in unit.lower():
                value *= 60
            entities['time'].append(value)
    
    # Process money patterns
    for pattern in money_patterns:
        money_matches = re.finditer(pattern, text)
        for match in money_matches:
            try:
                value = float(match.group(1))
                entities['money'].append(value)
            except ValueError:
                continue

    # Enhanced ingredient extraction
    ingredient_patterns = [
        r'(?:have|got|with)\s*((?:[a-zA-Z]+(?:,\s*)?)+)',
        r'ingredients?:?\s*((?:[a-zA-Z]+(?:,\s*)?)+)',
        r'using\s*((?:[a-zA-Z]+(?:,\s*)?)+)',
        r'cook(?:ing)?\s*with\s*((?:[a-zA-Z]+(?:,\s*)?)+)'
    ]
    
    # Combine SpaCy entities with pattern matching
    food_entities = set([ent.text.lower() for ent in doc.ents if ent.label_ in ['FOOD', 'PRODUCT']])
    
    for pattern in ingredient_patterns:
        matches = re.finditer(pattern, text_lower)
        for match in matches:
            ingredients = match.group(1).split(',')
            food_entities.update(ing.strip() for ing in ingredients)
    
    entities['ingredients'].extend(list(food_entities))

    # Enhanced goal extraction with variations
    goal_patterns = {
        'low_carb': r'low\s*carb|low\s*carbon?hydrates?',
        'high_protein': r'high\s*protein|protein\s*rich',
        'keto': r'keto(?:genic)?',
        'low_fat': r'low\s*fat|reduced\s*fat',
        'low_calorie': r'low\s*cal(?:orie)?s?|diet\s*friendly'
    }
    
    for goal, pattern in goal_patterns.items():
        if re.search(pattern, text_lower):
            entities['goal'] = goal
            break

    return entities

conversation_states = {}  # Dict to store state for each user
user_plans = dict()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_type = update.message.chat.type
    text = update.message.text
    response = None

    if message_type == 'supergroup':
        if USERNAME in text:
            text = text.replace(USERNAME, '').strip()
        else:
            return
    
    if user_id not in conversation_states:
        conversation_states[user_id] = ConversationState()
    
    state = conversation_states[user_id]
    state.last_activity = datetime.now()
    entities = extract_entities(text)
    
    # Handle initial state or command detection
    if state.current_state is None:
        if (entities['command_type'] == 'new_plan' or 
            text.startswith('/new') or 
            any(word in text.lower() for word in ['create', 'make', 'start'])):
            
            state.current_state = 'collecting_plan_info'
            state.pending_fields = {'name', 'time', 'budget', 'ingredients', 'goal'}
            state.collected_data = {}
            
            # Auto-fill detected entities
            if entities['time']:
                state.collected_data['time'] = entities['time'][0]
                state.pending_fields.remove('time')
            if entities['money']:
                state.collected_data['budget'] = entities['money'][0]
                state.pending_fields.remove('budget')
            if entities['ingredients']:
                state.collected_data['ingredients'] = entities['ingredients']
                state.pending_fields.remove('ingredients')
            if entities['goal']:
                state.collected_data['goal'] = entities['goal']
                state.pending_fields.remove('goal')
            
            # Ask for missing information
            if state.pending_fields:
                next_field = next(iter(state.pending_fields))
                response = get_prompt_for_field(next_field)
            else:
                try:
                    plan_name = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    add_plan(
                        plan_name,
                        state.collected_data['budget'],
                        state.collected_data.get('goal', 'None'),
                        state.collected_data['ingredients'],
                        state.collected_data['time']
                    )
                    response = create_success_message(plan_name, state.collected_data)
                    state.current_state = None
                    state.collected_data = {}
                except ValueError as e:
                    response = f"❌ Error creating plan: {str(e)}"
        else:
            response = handle_response(text)
    
    # Handle ongoing conversation
    elif state.current_state == 'collecting_plan_info':
        # Process input based on the pending field
        current_field = next(iter(state.pending_fields))
        
        if current_field == 'name':
            if len(text) > 30:
                response = "Plan name is too long. Please use a shorter name (max 30 characters)."
            else:
                state.collected_data['name'] = text
                state.pending_fields.remove('name')
        elif current_field == 'time' and entities['time']:
            state.collected_data['time'] = entities['time'][0]
            state.pending_fields.remove('time')
        elif current_field == 'budget' and entities['money']:
            state.collected_data['budget'] = entities['money'][0]
            state.pending_fields.remove('budget')
        elif current_field == 'ingredients' and ',' in text:
            ingredients = [i.strip() for i in text.split(',')]
            if ingredients:
                state.collected_data['ingredients'] = ingredients
                state.pending_fields.remove('ingredients')
        elif current_field == 'goal' and entities['goal']:
            state.collected_data['goal'] = entities['goal']
            state.pending_fields.remove('goal')
        elif text.lower() in ['cancel', 'stop', 'quit']:
            state.current_state = None
            response = "Plan creation cancelled."
            return
        
        # If current field wasn't handled, provide specific error message
        if current_field in state.pending_fields:
            response = get_error_message(current_field, text)
        
        # Generate next prompt or create plan
        if state.pending_fields and not response:
            next_field = next(iter(state.pending_fields))
            response = get_prompt_for_field(next_field)
        elif not state.pending_fields:
            try:
                plan_name = state.collected_data.get('name', f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                add_plan(
                    plan_name,
                    state.collected_data['budget'],
                    state.collected_data.get('goal', 'None'),
                    state.collected_data['ingredients'],
                    state.collected_data['time']
                )
                response = create_success_message(plan_name, state.collected_data)
                state.current_state = None
                state.collected_data = {}
            except ValueError as e:
                response = f"❌ Error creating plan: {str(e)}"

    if response:
        print("\tBot:", response, "\n")
        await update.message.reply_text(response)

def get_error_message(field: str, input_text: str) -> str:
    error_messages = {
        'time': "Please specify a valid time in minutes (e.g., '30 minutes' or '1 hour').",
        'budget': "Please specify a valid budget amount (e.g., '$20' or '15.50').",
        'ingredients': "Please provide ingredients separated by commas (e.g., 'chicken, rice, vegetables').",
        'goal': "Please specify a valid goal (low_carb, high_protein, keto, low_fat, or low_calorie).",
        'name': "Please provide a name for your meal plan (max 30 characters)."
    }
    return error_messages.get(field, "Invalid input. Please try again.")

def create_success_message(plan_name: str, data: dict) -> str:
    return (
        f"✅ Created plan: {plan_name}\n"
        f"⏰ Time: {data['time']} minutes\n"
        f"💰 Budget: ${data['budget']:.2f}\n"
        f"🥗 Ingredients: {', '.join(data['ingredients'])}\n"
        f"🎯 Goal: {data.get('goal', 'None')}"
    )
async def cleanup_old_conversations(context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now()
    for user_id, state in list(conversation_states.items()):
        if (current_time - state.last_activity).total_seconds() > 1800:  # 30 minutes
            del conversation_states[user_id]

async def create_plan(update: Update, state: ConversationState):
    try:
        plan_name = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        add_plan(
            plan_name,
            state.collected_data['budget'],
            state.collected_data.get('goal', 'None'),
            state.collected_data['ingredients'],
            state.collected_data['time']
        )
        await update.message.reply_text(
            f"✅ Created your meal plan with:\n"
            f"⏰ Time: {state.collected_data['time']} minutes\n"
            f"💰 Budget: ${state.collected_data['budget']}\n"
            f"🥗 Ingredients: {', '.join(state.collected_data['ingredients'])}\n"
            f"🎯 Goal: {state.collected_data.get('goal', 'None')}"
        )
        state.current_state = None
    except ValueError as e:
        await update.message.reply_text(f"❌ Error creating plan: {str(e)}")

def get_prompt_for_field(field: str) -> str:
    prompts = {
        'name': "What would you like to name this meal plan?",
        'time': "How much time do you have for cooking? (e.g., 30 minutes)",
        'budget': "What's your budget for this meal? (e.g., $20)",
        'ingredients': "What ingredients would you like to use? (separate with commas)",
        'goal': "What's your nutritional goal? (low_carb, high_protein, keto, low_fat, or low_calorie)"
    }
    return prompts.get(field, "Please provide more information.")

if __name__ == "__main__":
    print("Starting")
    app = Application.builder().token(TELETOKEN).read_timeout(30).write_timeout(30).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("custom", custom_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)
    
    # Create the event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Add cleanup task to the application's job queue instead
    app.job_queue.run_repeating(cleanup_old_conversations, interval=300)  # Run every 5 minutes
    
    print("Polling")
    app.run_polling(poll_interval=3)
