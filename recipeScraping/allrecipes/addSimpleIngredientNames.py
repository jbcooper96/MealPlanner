import pickle
import json
import pandas as pd

with open("ing_mappings_full.pkl", "rb") as file:
    loaded_dict = pickle.load(file)

def get_unique_ingredient_name_list(df):
    ingredients_set = set()
    for index, row in df.iterrows():
        ingredients = json.loads(row["ingredients"])
        for ingredient in ingredients:
            if "ingredient" in ingredient:
                if ingredient["ingredient"].lower() == "filling:":
                    print(ingredient)
                ingredients_set.add(ingredient["ingredient"].lower())

    return list(ingredients_set)

print(len(loaded_dict))

unique_ings = set()
cats = set()

for key in loaded_dict:
    unique_ings.add(loaded_dict[key]["simple_name"])
    cats.add(loaded_dict[key]["category"])



df = pd.read_csv("cleanedData1.csv")

amt = 0
unq_names = get_unique_ingredient_name_list(df)
for i in unq_names:
    if i not in loaded_dict.keys():
        print(i)
        amt += 1


drop_rows = []

new_ingredients = []
for index, row in df.iterrows():
    ingredients = json.loads(row["ingredients"])
    for ingredient in ingredients:
        drop = False
        if "ingredient" in ingredient:
            if ingredient["ingredient"].lower() == "optional garnishes: thinly sliced nori, cilantro, lime wedges, furikake seasoning":
                ing_names = ['nori' 'cilantro', 'lime']
                ingredient["base_ingredient"] = ing_names
                ingredient["category"] = "garnish"
            elif ingredient["ingredient"].lower() == "filling:":
                print(ingredient)
                drop_rows.append(index)
                drop = True
                break
            else:
                ing_name = ingredient["ingredient"].lower()
                ing_details = loaded_dict[ing_name]
                ingredient["base_ingredient"] = ing_details["simple_name"]
                ingredient["category"] = ing_details["category"]
    if not drop:
        new_ingredients.append(json.dumps(ingredients))

for row in drop_rows:
    df.drop(index=row, inplace=True)

df["ingredients"] = new_ingredients

df.to_csv("cleanedData3.csv", index=False)

print(unique_ings)