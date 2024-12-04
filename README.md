# Meal Planning Chatbot

A Telegram-based chatbot for meal planning, recipe suggestions, and budget management tailored to user dietary goals and preferences. This code will have to be running, with the proper API key of @CometFoodBot, for the account on Telegram to reply to messages.

## Project Overview
This chatbot assists users in managing their diet or lifestyle by providing recipes and meal plans that match fitness goals, dietary preferences, and budgets. It also helps users track some food expenses and find recipes based on available ingredients.

### Goal
Create a chatbot that suggests recipes in a meal plan, helps users manage their diet, and provides recipe recommendations to match their fitness goals, create plans, and track expenses.

## Youtube Video
https://youtube.com/shorts/Ln_xNlQvJtQ?feature=share

## Installation Instructions
1) Required libraries (pip install) to function:
numpy, torch,
nltk, spacy,
telegram, python-telegram-bot, "python-telegram-bot[job-queue]"
2) Download in the command line:
python -m spacy download en_core_web_sm
3) During the first time running, make sure that both lines inside nltk_utils.py will execute:
nltk.download('punkt')
nltk.download('punkt_tab')
4) Run train.py for the classifier file to be created, then telegram-bot.py.
5) After it prints "Polling", you may start chatting with @CometFoodBot in Telegram.

### Scope
The chatbot will work on the Telegram platform. Users will input commands or text queries in the form of:
- List of ingredients.
- Weekly/monthly budget and available cooking time.
- Basic diet goals (focus on vitamin/protein/calorie intake, vegan preferences, etc.).
The chatbot will respond with personalized recipe suggestions or ingredient recommendations tailored to the Plan specified by the user's situation.

### Value
- Personalized plans to support health goals, manage food finances, and address undernutrition.
- Suggestions for recipes using current ingredients or recommending replacements and long-term health-focused recipes.
- Ease of starting or maintaining certain lifestyle changes (e.g., vegetarianism, dieting, gym routines).

## Natural Language Processing Tasks
- **Nathaniel Pott**: Create some limited training data of typical user requests and developing the text classification method with a 2-layer network processing the user input, also a few Spacy/regex patterns that are used to get an understanding of the query intent before manipulating its components.
- **Fariz Ali**: Worked on classification and relation extraction by regular expression patterns and in Spacy to build the user plans which are used by the API to recommend recipes based on ingredients, cost, nutrition, user constraints.
- **Charles Whitworth**: Implement text generation techniques for changing state and responding/answering user queries about ingredients, recipes, diet, and nutrients.

## Data Sources
Leveraged the API from SpoonacularAPI to generate recipes based on the user input. 

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
