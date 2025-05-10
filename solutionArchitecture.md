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
