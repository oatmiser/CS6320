import math
import requests
from config import SPOONACULAR_API_KEY

class UserPlan:
    def __init__(self, name:str, budget:float = 0, goal:str = "None", ingredients:list = []):
        self.name = name
        self.budget = budget
        self.goal = goal
        self.ingredients = ingredients
        self.recipes = []

    def display(self):
        str_build = f"Plan {self.name}:\n"
        for attr in ['budget', 'goal', 'ingredients']:
            str_build += f"\t{attr}: {getattr(self, attr)}\n"

        if self.recipes:
            str_build += "\tRecipes:\n"
            for recipe in self.recipes:
                str_build += f"\t- {recipe['title']}\n"
        else:
            str_build += "\tNo recipes fetched yet.\n"

        print(str_build)

    def setName(self, name:str):
        self.name = name
    def setBudget(self, amount:float):
        self.budget = amount
    def setGoal(self, desc:str):
        self.goal = desc
    def setIngredients(self, food:list):
        self.ingredients = food

    def fetch_recipes(self):
        # Build the query parameters
        params = {
            'apiKey': SPOONACULAR_API_KEY,
            'ingredients': ','.join(self.ingredients),
            'number': 5,
            'ranking': 2,
            'ignorePantry': True,
        }

        # Add dietary goals if specified
        if self.goal.lower() != 'none':
            params['diet'] = self.goal.lower()

        # Make the API request
        response = requests.get('https://api.spoonacular.com/recipes/findByIngredients', params=params)

        if response.status_code == 200:
            self.recipes = response.json()
            print(f"Found {len(self.recipes)} recipes for plan '{self.name}'.")
        else:
            print(f"Error fetching recipes: {response.status_code} - {response.text}")
            self.recipes = []

def fetch_recipe_details(recipe_id):
    params = {
        'apiKey': SPOONACULAR_API_KEY,
        'includeNutrition': True,
    }
    response = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching recipe details: {response.status_code} - {response.text}")
        return None

def display_recipe_details(recipe):
    if recipe:
        print(f"\nTitle: {recipe.get('title', 'N/A')}")
        print(f"Ready in: {recipe.get('readyInMinutes', 'N/A')} minutes")
        print(f"Servings: {recipe.get('servings', 'N/A')}")

        price_per_serving = recipe.get('pricePerServing', None)
        if price_per_serving is not None:
            print(f"Price per Serving: ${price_per_serving / 100:.2f}")
        else:
            print("Price per Serving: N/A")

        print("\nIngredients:")
        for ingredient in recipe.get('extendedIngredients', []):
            print(f"- {ingredient.get('original', 'N/A')}")

        print("\nInstructions:")
        instructions = recipe.get('instructions') or 'No instructions available.'
        print(instructions.strip())

        print("\nNutritional Information:")
        nutrients = recipe.get('nutrition', {}).get('nutrients', [])
        if nutrients:
            for nutrient in nutrients:
                print(f"{nutrient.get('name', 'N/A')}: {nutrient.get('amount', 'N/A')}{nutrient.get('unit', '')}")
        else:
            print("Nutritional information is not available.")
    else:
        print("No details to display.")

user_plans = dict()
def add_plan(name:str, budget:float, goal:str, ingredients:list):
    global user_plans
    user_plans[name] = UserPlan(name, budget, goal, ingredients)

if __name__ == "__main__":
    while True:
        user_choice = input("\n#-# Command (new, edit, forget, show, recipes, quit): ").upper()
        if user_choice == "QUIT":
            break
        elif user_choice == "NEW":
            args = input("Enter name [budget] [goal] [(ingredient,)+ingredient]: ")
            split = args.split(" ")

            name = split[0]
            budget = 0
            goal = "None"
            ingredients = list()
            if len(split) > 1:
                for token in split[1:]:
                    try:
                        budget = float(token)
                    except ValueError:
                        if "," in token:
                            ingredients = token.split(",")
                        else:
                            goal = token

            if name in user_plans:
                confirm = input(f"Plan {name} already exists, overwrite?\nY/N: ")
                if confirm[0].lower() == "y":
                    add_plan(name, budget, goal, ingredients)
                    user_plans[name].fetch_recipes()
                    print(f"Plan {name} was updated.")
                else:
                    print(f"Plan {name} is unchanged.")
            else:
                add_plan(name, budget, goal, ingredients)
                user_plans[name].fetch_recipes()
                print(f"Plan {name} was created.")

        elif user_choice == "EDIT":
            search = input("Enter plan name: ")
            if search in user_plans:
                plan_obj = user_plans[search]
                plan_obj.display()
                update = input("Select a variable to update: ")

                if update in dir(plan_obj):
                    new_value = input(f"\tChange {update} to: ")
                    if update == 'budget':
                        plan_obj.setBudget(float(new_value))
                    elif update == 'goal':
                        plan_obj.setGoal(new_value)
                    elif update == 'ingredients':
                        if ',' in new_value:
                            ingredients = new_value.split(',')
                        else:
                            ingredients = new_value.split()
                        plan_obj.setIngredients(ingredients)
                    else:
                        print(f"Cannot update {update}.")
                    # Fetch updated recipes
                    plan_obj.fetch_recipes()
                else:
                    print(f"Sorry, {update} is not a member of Plan {search}.")
            else:
                print("Sorry, this plan does not exist!")

        elif user_choice == "SHOW":
            plan_name = input("Enter plan name (leave blank to show all): ")
            if len(plan_name) == 0:
                for obj in user_plans.values():
                    obj.display()
            else:
                if plan_name in user_plans:
                    user_plans[plan_name].display()
                else:
                    print(f"Plan {plan_name} does not exist.")

        elif user_choice == "FORGET":
            search = input("Enter plan to remove: ")
            if search in user_plans:
                confirm = input(f"Do you really want to remove Plan {search}?\nY/N: ")
                if confirm[0].lower() == "y":
                    user_plans.pop(search)
                    print(f"Plan {search} was removed.")
                else:
                    print(f"Plan {search} was NOT removed.")
            else:
                print("Sorry, this plan does not exist!")

        elif user_choice == "RECIPES":
            plan_name = input("Enter plan name to view recipes: ")
            if plan_name in user_plans:
                plan = user_plans[plan_name]
                if plan.recipes:
                    for idx, recipe in enumerate(plan.recipes):
                        print(f"{idx + 1}. {recipe['title']}")
                    choice = int(input("Enter the number of the recipe to view details: ")) - 1
                    if 0 <= choice < len(plan.recipes):
                        recipe_id = plan.recipes[choice]['id']
                        recipe_details = fetch_recipe_details(recipe_id)
                        display_recipe_details(recipe_details)
                    else:
                        print("Invalid selection.")
                else:
                    print("No recipes available for this plan.")
            else:
                print("Plan not found.")

        else:
            print("Invalid command.")
