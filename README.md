README

### Get Started
- To get started right now, visit https://meal-planning-ai-tool.onrender.com
- The free tier for the Spoonacular API has a limited number of tokens. If the publically hosted URL above is saying that there are no more tokens for the day, follow the steps below to set up the project locally and add your own spoonacular and groq keys
1. Clone the repo. Navigate to desired location and paste this into your terminal:
  ```git clone https://github.com/JesseLevitas/meal-planning-ai-tool.git```
2. Create and activate a virtual environment
   ```python3 -m venv venv && source venv/bin/activate```
3. Paste the following line in your terminal:
   ```pip install -r requirements.txt```
4. Create .env file. Paste this in terminal: ```cp .env.example .env``` and navigate to the new .env file. Fill in with your own api keys and set USE_TEST_DATA to false.
- Troubleshooting tip: the terminal will output the value of USE_TEST_DATA. If it doesn't match what is in .env for some reason, simply enter this into the terminal: ```unset USE_TEST_DATA``` and run the app again.

- #### How to set up Groq and Spoonacular Keys (optional)
- If you want to use live data, but my account is out of tokens, you will need to make your own accounts

- Groq: make a free account here, get your api key, and paste it into the .env file: https://console.groq.com/home
- Same thing for spoonacular here: https://spoonacular.com/food-api/console#Dashboard

5. Run the app using ```python main.py``` and navigate to the address that it is running on using any browser (should be output right after running this in terminal)

### Note:
- There might be an error once in a while caused by the way Groq responds. If this happens, just click on "generate plan" again or reload the page.


