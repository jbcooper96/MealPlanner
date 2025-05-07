import pandas as pd
import json

ALL_MEALS = ["Appetizers & Snacks", "Lunch", "Breakfast & Brunch", "Dinner", "Desserts"]

with open("recipes.json") as recipe_file:
    json_data = json.loads(recipe_file.read())


df = pd.DataFrame(json_data)
print(df.iloc[0])

new_df = pd.DataFrame()

recipe_name_to_index = dict()
titles = []
ingredients = []
instructions = []
nutritionFacts = []
tags = []
meal = []

i = 0
meals = []
for _, row in df.iterrows():
    if row["title"] in recipe_name_to_index:
        index = recipe_name_to_index[row["title"]]
        row_tags = row["tags"]
        tags[index] += row_tags
        for meal in ALL_MEALS:
            if meal in row["tags"]:
                meals[index] = meal
                break
    else:
        titles.append(row["title"])
        ingredients.append(json.dumps(row["ingredients"]))
        instructions.append(row["instructions"])
        nutritionFacts.append(row["nutritionFacts"])
        tags.append(row["tags"])

        found_meal = False
        for meal in ALL_MEALS:
            if meal in row["tags"]:
                meals.append(meal)
                found_meal = True
                break
        if not found_meal:
            meals.append("")

        recipe_name_to_index[row["title"]] = i
        i += 1

new_df["title"] = titles
new_df["ingredients"] = ingredients
new_df["instructions"] = instructions
new_df["nutritionFacts"] = nutritionFacts
new_df["tags"] = tags
new_df["meal"] = meals

new_df.to_csv("cleanedData.csv")

print(new_df.head(10))