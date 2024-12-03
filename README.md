# Meal Planning Chatbot

A Telegram-based chatbot for meal planning, recipe suggestions, and budget management tailored to user dietary goals and preferences. This code will have to be running, with the proper API key of @CometFoodBot, for the account on Telegram to reply to messages.

## Project Overview
This chatbot assists users in managing their diet or lifestyle by providing recipes and meal plans that match fitness goals, dietary preferences, and budgets. It also helps users track some food expenses and find recipes based on available ingredients.

### Goal
Create a chatbot that suggests recipes in a meal plan, helps users manage their diet, and provides recipe recommendations to match their fitness goals, create plans, and track expenses.

## Youtube Video
https://youtube.com/shorts/Ln_xNlQvJtQ?feature=share

### Scope
The chatbot will work on the Telegram platform. Users will input commands or text queries in the form of:
- List of ingredients.
- Weekly/monthly budget and available cooking time.
- Basic diet goals (focus on vitamin/protein/calorie intake, vegan preferences, etc.).
- Special/temporary events (e.g., breakfast, gym, outdoor day).

The chatbot will respond with personalized recipe suggestions or ingredient recommendations tailored to the Plan specified by the user's situation.

### Value
- Personalized plans to support health goals, manage food finances, and address undernutrition.
- Suggestions for recipes using current ingredients or recommending replacements and long-term health-focused recipes.
- Ease of starting or maintaining certain lifestyle changes (e.g., vegetarianism, dieting, gym routines).

## Project Tasks and Responsibilities

### Natural Language Processing (NLP) Tasks
- **Nathaniel Pott**: Text summarization and classification for processing data sources.
- **Fariz Ali**: Classification and relation extraction to recommend ingredients based on cost, nutrition, and user constraints.
- **Charles Whitworth**: Question answering related to nutrition and budgeting of various ingredients.
- **Everyone**: Text generation for queries related to ingredients, recipes, diet, exercise, and nutrients.

## Data Sources
The project will use the following data sources:
- Fitness/lifestyle/cooking/dieting books.
- Fitness/cooking/dieting blogs.
- Publicly available diet-specific recipes.
- Literature on ingredient pairings and combinations (e.g., *The Flavor Bible*).

## Installation Instructions
Create a config.py locally and add the keys for Telegram bot and SpoonacularAPI in it and then run the 6320-telegram-updated.py file


## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
