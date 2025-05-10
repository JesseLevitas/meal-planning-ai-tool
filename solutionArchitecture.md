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

### Frontend (HTML + Tailwind CSS + JS):
- Form to choose diet, exclusions, and number of people
- Dynamic UI showing chosen recipes, images, and grocery list with checkboxes
### Backend (Flask + Python):
- Handles form submission, API calls, error handling, and data orchestration
- Includes logic for both real API use and fallback to test data
### LLM Integration (Groq):
- Groups recipes into meals (breakfast/lunch/dinner) via prompt
- Helps structure logic for serving size balancing and planning
- tons of other uses for later versions. For example:
  - suggest substitutions for ingredients
  - cost estimation
  - can answer recipe instruction questions
  - translate grocery list quantities into purchasable quantities(i.e. 4.50 cups of milk -> minimum purchasable quantity = half-gallon)
### Spoonacular API:
- Fetches detailed recipe data and ingredient lists
- Can filter based on diets or excluded ingredients

This is a visual showing the flow of data in this web app:

![flow](https://github.com/user-attachments/assets/3179b3a1-9754-4a09-8543-c892bdb737fc)
