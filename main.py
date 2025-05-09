from collections import defaultdict
from fractions import Fraction
from flask import Flask, render_template, request
import requests
from groq import Groq
from dotenv import load_dotenv
import json, os, re
import itertools
from test_data import meals, meal_images, ingredient_list
from ignored_ingredients import l


load_dotenv()
# load API keys:
USE_TEST_DATA = os.getenv("USE_TEST_DATA", "true").lower() == "true"
print("USE_TEST_DATA =", USE_TEST_DATA)
SPOONACULAR_KEY = os.getenv("SPOONACULAR_API_KEY")
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
MODEL_ID = "llama3-70b-8192"
UNIT_ALIAS = {
    "tsp": "teaspoon",
    "teaspoons": "teaspoon",
    "Tbsp": "tablespoon",
    "tablespoons": "tablespoon",
    "tbsp": "tablespoon",
    "cup": "cups",
    "cloves": "clove",
    }


##################################################################
#
# app setup
#


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    message = None

    if request.method == "POST":
        diet       = request.form.get("diet")
        exclusions = request.form.get("exclusions")

        try:
            num_people = int(request.form.get("people") or 1)
            if num_people < 1:
                raise ValueError
        except ValueError:
            message = "Please enter a valid number of people (1 or more)."
            return render_template("index.html", message=message)

       
        if USE_TEST_DATA:
            meals_local        = meals
            meal_images_local  = meal_images
            ingredient_local   = ingredient_list
        else:
            try:
                meal_plan = get_meal_plan(diet, exclusions, num_people)
                meals_local        = meal_plan["meals"]
                meal_images_local  = meal_plan["meal_images"]
                ingredient_local   = meal_plan["ingredient_list"]
            except Exception as e:
                message = f"Error fetching data from Spoonacular: {e}"
                return render_template("index.html", message=message)

        try:
            title_to_url = {}
            title_to_img = {}
            for m_str, img_url in zip(meals_local, meal_images_local):
                d = parse_meal_string(m_str)
                title_to_url[d["title"]] = d["url"]
                title_to_img[d["title"]] = img_url or "/static/img/placeholder.png"

            ingredient_lookup = {
                rec["recipe_title"]: rec["ingredients"]
                for rec in ingredient_local
            }
        except Exception as e:
            message = f"Error preparing data: {e}"
            return render_template("index.html", message=message)

        try:
            grouped_json = group_meals(meals_local, ingredient_local)
            data         = parse_json(grouped_json)
            selected     = select_meals(data, num_people)
            grocery_raw  = update_ingredients(selected, ingredient_lookup, num_people)
        except Exception as e:
            message = f"Meal grouping or ingredient calculation failed: {e}"
            return render_template("index.html", message=message)

        try:
            meal_titles, recipe_assets, recipe_images, recipe_urls, meal_servings = [], [], [], [], []

            for slot in ("breakfast", "lunch", "dinner"):
                for rec in selected[slot]["recipes"]:
                    title    = rec["title"]
                    servings = rec["servings"]
                    url      = title_to_url.get(title, "#")
                    img      = title_to_img.get(title, "/static/img/placeholder.png")

                    meal_titles.append(f"{title} (serves {servings})")
                    meal_servings.append(servings)
                    recipe_assets.append(f"{title} (serves {servings}) ({url})")
                    recipe_images.append(img)
                    recipe_urls.append(url)

            return render_template(
                "index.html",
                meals         = recipe_assets,
                meal_titles   = meal_titles,
                meal_servings = meal_servings,
                meal_images   = recipe_images,
                recipe_urls   = recipe_urls,
                groceries     = grocery_raw,
                message       = message,
            )
        except Exception as e:
            message = f"Failed to build output cards: {e}"
            return render_template("index.html", message=message)

    return render_template("index.html", message=message)


##################################################################
#
# get_meal_plan
#


def get_meal_plan(diet, exclusions, num_people):
    """
    Generates a weekly meal plan and gathers detailed ingredient information.
    Calls Spoonacular API
    Only runs if USE_TEST_DATA flag set to false

    Parameters
    ----------
    diet: dietary preference (e.g., "vegetarian", "keto"). Can be empty (str)
    exclusions: comma-separated list of excluded ingredients. Can be empty (str)
    num_people: Number of people to plan meals for (int)

    Returns
    -------
    dict
        {
            "meals": list of meal descriptions with servings and source URLs (str),
            "meal_images": list of meal images
            "ingredient_list": list of ingredients grouped by recipe (str),
            "total_servings": total number of servings across all meals (int),
            "people": number of people (int),
            "target_servings": expected total servings (num_people * 21) (int)
        }
    """
    url = "https://api.spoonacular.com/mealplanner/generate"
    params = {
        "apiKey": SPOONACULAR_KEY,
        "timeFrame": "week",
        "diet": diet or "",
        "targetCalories": 2000,
    }

    resp = requests.get(url, params=params)
    if resp.status_code != 200:
        return {
            "meals": [f"Error {resp.status_code} {resp.text}"],
            "meal_images": [],
            "ingredient_list": [],
            "total_servings": 0,
            "people": num_people,
            "target_servings": num_people * 21,
        }

    data = resp.json()

    meal_ids = [
        str(meal["id"])
        for day in data.get("week", {}).values()
        for meal in day.get("meals", [])
    ]

    meals          = []
    meal_images    = []
    grocery_items  = []
    total_servings = 0

    if meal_ids:
        bulk_url    = "https://api.spoonacular.com/recipes/informationBulk"
        bulk_params = {"apiKey": SPOONACULAR_KEY, "ids": ",".join(meal_ids)}
        bulk_resp   = requests.get(bulk_url, params=bulk_params)

        if bulk_resp.status_code == 200:
            for recipe in bulk_resp.json():
                title      = recipe["title"]
                servings   = recipe.get("servings", 1)
                source_url = recipe.get("sourceUrl", "#")
                image_url  = recipe.get("image", "")

                meals.append(f"{title} (serves {servings}) ({source_url})")
                meal_images.append(image_url)
                total_servings += servings

                ingredients = [
                    {
                        "name": ing.get("name", ""),
                        "amount": ing.get("amount", 1),
                        "unit": ing.get("unit", ""),
                    }
                    for ing in recipe.get("extendedIngredients", [])
                ]

                grocery_items.append(
                    {
                        "recipe_title": title,
                        "servings": servings,
                        "ingredients": ingredients,
                    }
                )
        else:
            total_servings = 21  # simple fallback

    return {
        "meals": meals,
        "meal_images": meal_images,      
        "ingredient_list": grocery_items,
        "total_servings": total_servings,
        "people": num_people,
        "target_servings": num_people * 21,
    }


##################################################################
#
# group_meals
#


def group_meals(meals, ingredient_list):
    """
    Prompts Groq to group recipes by meal type 

    Parameters
    ----------
    meals: list of recipes
    ingredient_list: list of ingredients (with quantities) grouped by recipe

    Returns
    ---------
    response from groq (str)
    """

    grocery_text = ""
    for recipe in ingredient_list:
        grocery_text += f"Recipe: {recipe['recipe_title']} (serves {recipe['servings']})\n"
        for ingredient in recipe['ingredients']:
            amount = ingredient['amount']
            unit = ingredient['unit']
            name = ingredient['name']
            grocery_text += f"- {amount} {unit} {name}\n"
        grocery_text += "\n"

    prompt = (
        "Here is a meal plan and ingredient list.\n\n"
        "Meals:\n"
        + "\n".join(meals) +
        "\n\nGrocery List:\n"
        + grocery_text +
        "\n\n"
        "Group the recipes into two categories: breakfast_dessert or lunch_dinner"
        '''
        Output your answer as JSON like this:
        {
        "breakfast_dessert": [
            {"title": "Recipe Name", "servings": servings_number},
            ...
        ],
        "lunch_dinner": [
            {"title": "Recipe Name", "servings": servings_number},
            ...
        ]
        }"
        '''
    )

    response = groq_client.chat.completions.create(
        model=MODEL_ID, 
        messages=[
            {"role": "system", "content": "You are an expert meal planner and nutrition assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


##################################################################
#
# parse_json
#

def parse_json(response: str):
    """
    Parses groq response and calls safe_json_load to load safely

    Parameters
    -----------
    response: groq response with meal groupings (str)

    Returns
    ----------
    JSON formatted groupings
    """

    json_start = response.find("{")
    json_end   = response.rfind("}") + 1
    json_str   = response[json_start:json_end]
    return safe_json_load(json_str)


##################################################################
#
# group_meals
#


def select_meals(data, num_people):
    """
    Selects meals and scales recipes to match number of people

    Parameters
    -----------
    data: parsed recipes JSON (dict)
    num_people: number of people user is cooking for (int)

    Returns
    ---------
    chosen: JSON of chosen recipes by meal block (breakfast, lunch, dinner) with servings. Scaled to fit # of people eating. (dict)
    """

    breakfast_recipes, breakfast_total = best_subset(
        data["breakfast_dessert"]
    )

    lunch_recipes, lunch_total = best_subset(
        data["lunch_dinner"]
    )

    # remove chosen lunches so dinners don't duplicate
    lunch_titles = {r["title"] for r in lunch_recipes}
    remaining_ld = [r for r in data["lunch_dinner"]
                    if r["title"] not in lunch_titles]

    dinner_recipes, dinner_total = best_subset(
        remaining_ld
    )

    chosen = {
        "breakfast": {
            "recipes": breakfast_recipes,
            "total_servings": breakfast_total
        },
        "lunch": {
            "recipes": lunch_recipes,
            "total_servings": lunch_total
        },
        "dinner": {
            "recipes": dinner_recipes,
            "total_servings": dinner_total
        }
    }

    for i in chosen.values():
        for r in i["recipes"]:
            r["servings"] *= num_people
    
    for i in chosen.values():
        total = sum(r["servings"] for r in i["recipes"])
        i["total_servings"] = total

    return chosen


##################################################################
#
# get_ingredients
#


def get_ingredients(title: str, lookup: dict):
    """
    Return ingredient list for a recipe title using exact, case‑insensitive,
    or contains() match.  Filters out ingredients like water, salt, etc. Returns None if nothing found.

    Parameters
    ------------
    title: recipe title (str)
    lookup: dict of titles (key) and ingredients (value) (dict)

    Returns
    ---------
    filtered recipe ingredients
    """
    rec_ing = None

    # 1. exact key
    if title in lookup:
        rec_ing = lookup[title]

    else:
        lowered = title.lower()

        # 2. exact, case-insensitive
        for key in lookup:
            if key.lower() == lowered:
                rec_ing = lookup[key]
                break

        # 3. substring fallback
        if rec_ing is None:
            for key in lookup:
                if lowered in key.lower():
                    rec_ing = lookup[key]
                    break

    if rec_ing is None:
        return None

    filtered = [
        ing for ing in rec_ing
        if ing.get("name", "").strip().lower() not in l
    ]
    return filtered


##################################################################
#
# update_ingredients
#


def update_ingredients(selected_meals, ingredient_lookup, num_people=1):
    """
    Combine & scale ingredients for chosen recipes.
    Returns {item_name: {unit: total_float_amount}} or flattened strings.

    Parameters
    ----------
    selected_meals: meals chosen from select_meals() (dict)
    ingredient_lookup: dict of titles (key) and ingredients (value) (dict)
    num_people: number of people (int)

    Returns
    --------
    {item_name: {unit: total_float_amount}} or flattened strings.
    """

    totals   = defaultdict(lambda: defaultdict(float))
    skipped  = []

    for meal_block in selected_meals.values():
        if not isinstance(meal_block, dict):
            continue

        for rec in meal_block["recipes"]:
            title  = rec["title"]
            scale  = rec.get("scale", 1) * num_people

            ing_list = get_ingredients(title, ingredient_lookup)
            if ing_list is None:
                skipped.append(title)
                continue

            for ing in ing_list:
                amt  = to_float(ing["amount"]) * scale
                unit = normalise_unit(ing["unit"])
                name = ing["name"].strip().lower()

                totals[name][unit] += amt

    # flatten single‑unit items
    combined = {}
    for name, units in totals.items():
        if len(units) == 1:
            u, a = next(iter(units.items()))
            combined[name] = f"{a:.2f} {u}"
        else:
            combined[name] = {u: round(a, 2) for u, a in units.items()}

    # log any missing recipes
    if skipped:
        print("[WARN] Missing ingredient lists for:", ", ".join(skipped))

    return combined


##################################################################
#
# helper functions
#


def safe_json_load(s: str):
    """
    Loads JSON of groq resonse. Ensures response is in correct format.
    Return best-effort JSON dict or raise error. 
    
    Paramaters
    -----------
    s: response from groq (str)

    Returns
    ---------
    JSON formatted groupings (dict)
    """
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        last = s.rfind("}")
        if last == -1:
            raise
        cleaned = s[: last + 1]
        return json.loads(cleaned)


def best_subset(recipes, min_rec=2, max_rec=3):
    """
    Pick 2–3 whole recipes whose combined servings:
      1. equal 7  (ideal) OR
      2. are the largest total < 7
      3. are the smallest total > 7 OR
    If several subsets tie, choose the one with fewer recipes.

    Parameters
    -----------
    recipes: JSON formatted recipe data (dict)
    min_rec: min value of size of subset (defaults to 2)
    max_rec: max value of size of subset (defaults to 3)

    Returns
    ---------
    subset of recipes (dict)
    number of servings (int)
    """

    below, above = None, None

    # iterate only over subsets between sizes min_rec and max_rec
    for r in range(min_rec, max_rec + 1):
        for combo in itertools.combinations(recipes, r):
            total = sum(item["servings"] for item in combo)

            if total == 7:
                return list(combo), total

            if total < 7:
                if (below is None or total > below[1]
                        or (total == below[1] and len(combo) < len(below[0]))):
                    below = (list(combo), total)

            if total > 7:
                if (above is None or total < above[1]
                        or (total == above[1] and len(combo) < len(above[0]))):
                    above = (list(combo), total)

    return below if below else above

def normalise_unit(u: str) -> str:
    """
    accounts for variations such as tbsp, tbsps, tablespoons...
    """
    return UNIT_ALIAS.get(u.lower(), u.lower() or "-")

def to_float(x: str) -> float:
    """
    converts values to floats to combine requirements for grocery list
    """
    try:
        return float(x)
    except ValueError:
        try:
            return float(Fraction(x))
        except Exception:
            return 1.0

RE_MEAL = re.compile(
    r"^(?P<title>.+?)\s+\(serves\s+(?P<servings>\d+)\)\s+\((?P<url>https?://[^\)]+)\)$"
)

def parse_meal_string(s: str):
    """
    parses recipe links
    """
    m = RE_MEAL.match(s.strip())
    if not m:
        raise ValueError(f"Cannot parse meal string: {s}")
    return {
        "title":     m.group("title"),
        "servings":  int(m.group("servings")),
        "url":       m.group("url"),
        "image":     "/static/placeholder.jpg"   # fill with real URL if you have it
    }

if __name__ == "__main__":
    app.run(debug=True)