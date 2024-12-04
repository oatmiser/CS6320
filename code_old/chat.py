import random
import json
import torch
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
with open('recipe-intents.json', 'r') as json_data:
    intents = json.load(json_data)

# 2 layer NN to classify a user query an Intent label
FILE = "data.pth"
data = torch.load(FILE)
input_size = data["input_size"]
hidden_size = data["hidden_size"]
output_size = data["output_size"]
all_words = data['all_words']
tags = data['tags']
model_state = data["model_state"]
model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


import requests
SPOONACULAR_API_KEY = '0bc3342c1e554cbca03a8365f408c220'
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
def get_mealdb(url:str):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            posts = response.json()
            return posts
        else:
            print('Error:', response.status_code)
            return None
    except requests.exceptions.RequestException as e:
        print('Error:', e)
        return None

bot_name = "CometFoodBot"
print("Let's chat! (type 'quit' to exit)")
ingredients = list()
state = 'start'
while True:
    sentence = input("You: ")
    if sentence == "quit":
        break


    if state == 'define_plan':
        ingredients = 'chicken,cheese,sauce'.split(',')
    elif state == 'edit_plan':
        query = sentence
        split = query.split(' ')
        if 'change' in split:
			# change x to y
            i = split.index('change')
            x = split[i+1]
            y = split[i+3]
            ingredients[ingredients.index(x)] = y
        elif 'switch' in split:
			# switch x and y
            i = split.index('switch')
            x = split[i+1]
            y = split[i+3]
            ingredients[ingredients.index(x)] = y
        elif 'instead' in split:
			# y instead of x
            i = split.index('instead')
            y = split[i-1]
            x = split[i+2]
            ingredients[ingredients.index(x)] = y
        elif 'replace' in split:
			# replace x with y
            i = split.index('replace')
            x = split[i+1]
            y = split[i+3]
            ingredients[ingredients.index(x)] = y
        elif 'add' in split:
            i = split.index('add')
            x = split[i+1]
            ingredients.append(x)
        elif 'remove' in split:
            pass
        elif 'delete' in split:
            pass
        print(f'Okay, you plan now has {y} instead of {x}')

    sentence = tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _,predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]
    if prob.item() > 0.75:
        # predicted label is likely correct so choose some response given for it from the json file
        for intent in intents['intents']:
            if tag == intent["tag"]:
                print(f"{bot_name}: {random.choice(intent['responses'])}")
    else:
        print(f"{bot_name}: I do not understand...")
        continue

    # make_food_plan
    match tag:
        case "greeting":
            pass
        case "goodbye":
            exit()
        case "thanks":
            pass
        case "random":
            #print(f"{bot_name}: I can recommend recipes, help you plan meals, or share cooking tips!")
            posts = get_mealdb('https://www.themealdb.com/api/json/v1/1/random.php')
            if posts:
                #print('First Post Title:', posts[0]['title'])
                #print('First Post Body:', posts[0]['body'])
                rand_recipe = posts['meals'][0]
                print(f"\n\t'{rand_recipe['strMeal']}' is a {rand_recipe['strArea']} meal in the {rand_recipe['strCategory']} category")
                if input(f'\n{bot_name}: Would you like to view its details? y/n: ').lower() == 'y':
                    ingredients = list()
                    for i in range(20): # maximum saved by MealDB
                        key = f'strIngredient{i+1}'
                        if rand_recipe[key] == "":
                            break
                        ingredients.append(rand_recipe[key])
                    print('\nIngredients: ' + ', '.join(ingredients))
                    #direct = '.\n'.join(rand_recipe['strInstructions'].split('.'))
                    direct = rand_recipe['strInstructions']
                    print(f"\nDirections:\n{direct}\n")
            else:
                print('Sorry, I am unable to access that information right now.')

        case "make_food_plan":
            #print(f"{bot_name}: Sure! Let me know your preferences or dietary goals.")
            state = 'define_plan'
        case "edit_food_plan":
            #print(f"{bot_name}: What changes would you like to make to your meal plan?")
            print(", ".join(ingredients))
            state = 'edit_plan'
        case "delete_food_plan":
            print(f"{bot_name}: Your meal plan has been removed.")
        case "generate_recipes_from_plan":
            print(f"{bot_name}: Here are some recipes based on your meal plan!")
        case _:
            print(f"{bot_name}: I'm not sure how to respond to ({tag}).")
