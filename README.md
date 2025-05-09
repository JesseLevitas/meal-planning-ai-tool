README

### Problem Statement

For busy college students and other individuals, planning a week’s worth of meals can be overwhelming. People often:

- Don't know where to start looking for recipes
- Struggle to build organized grocery lists
- Buy too much or too little due to poor portion planning
- Think cooking good food is too hard

Almost half of the people I interviewed don't make a grocery list before shopping! 

### Solution

My solution handles the planning and list generation for you!

This project addresses those challenges by using AI to generate a personalized meal plan and a consolidated grocery list that fits the user's diet, exclusions, and household size.


### Solution Design

### Inputs
- **Dietary Preference** (optional): e.g., vegetarian, keto
- **Excluded Ingredients** (optional): comma-separated list, e.g., peanuts, gluten
- **Number of People**: used to scale meals and ingredients

### LLM Prompt
The app sends a curated list of recipes and ingredients to a language model (Groq / LLaMA 3) and has it classify meals as either a breakfast option or a lunch/dinner option

### Tools
- **Recipe Fetcher**: Calls the Spoonacular API to generate a weekly plan and bulk fetch recipe metadata (title, servings, URL, ingredients, image).
- **Ingredient Scaler**: Consolidates and scales ingredients based on the number of people.
- **Meal Grouper (LLM Tool)**: Uses a structured LLM call to categorize meals into breakfast/lunch/dinner.
- **Meal Selecter**: iterates over meals to choose enough servings for 1 weeks worth of breakfasts, lunches, and dinners depending on number of people.
- **Frontend Toggle (for local use, if my api key runs out)**: Allows switching between live API data and offline demo data for limited usage environments.

### Outputs
- **Selected Recipes**: A selection of breakfast, lunch, and dinner recipes
- **Grocery List**: A combined list of all ingredients with normalized units and quantities (for the most part). Includes interactive checkboxes for shopping or printing.
- **Interactive UI**: Allows users to view images, visit source recipe pages, and interact with a simple meal plan and grocery interface.

### Get Started

- To get started right now, visit https://meal-planning-ai-tool.onrender.com
- The free tier for the Spoonacular API has a limited number of tokens. If the publically hosted URL above does not work, follow the steps below to set up the project locally and use hard-coded test data instead (or add your own spoonacular and groq keys)
1. clone the repo. Navigate to desired location and paste this into your terminal:
  ```git clone https://github.com/your-username/meal-planning-ai-tool.git```
2. Create and activate a virtual environment
   ```python3 -m venv venv && source venv/bin/activate```

- # How to set up Groq and Spoonacular Keys

