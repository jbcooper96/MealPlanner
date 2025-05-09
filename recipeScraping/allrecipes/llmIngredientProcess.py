import pandas as pd
from openai import OpenAI
from pydantic import BaseModel
import json
import pickle

class Ingredient(BaseModel):
    full_name: str
    simple_name: str
    category: str
    




def get_unique_ingredient_name_list(df, ings_already_processed):
    ingredients_set = set()
    for index, row in df.iterrows():
        ingredients = json.loads(row["ingredients"])
        for ingredient in ingredients:
            if "ingredient" in ingredient:
                if ingredient["ingredient"].lower() not in ings_already_processed.keys():
                    ingredients_set.add(ingredient["ingredient"].lower())

    return list(ingredients_set)

df = pd.read_csv("cleanedData1.csv")

with open("ing_mappings_full.pkl", "rb") as file:
    ing_map = pickle.load(file)

unique_ingredients = get_unique_ingredient_name_list(df, ing_map)

print(len(unique_ingredients))

client = OpenAI(base_url="http://localhost:1234/v1", api_key="none")

def get_ings_map(ings):
    completion = client.chat.completions.create(
        model="qwen3-32b",
        messages=[
            {"role": "system", "content": "You are a cooking assistant. Your job is to simplify ingredient names. The user will give you a list of ingredients and you will output a simplified and singular name and a category. For example for \"eggs, separated, divided\" just output \"egg\" /nothink"},
            {"role": "user", "content": json.dumps(ings)}
        ],
        temperature=0.7,
    )
    return json.loads(completion.choices[0].message.content)





BATCH_SIZE = 10
print(unique_ingredients)
batch = []
for i, un_ing in enumerate(unique_ingredients):
    batch.append(un_ing)
    if len(batch) == BATCH_SIZE:
        fail = True
        print(len(unique_ingredients) - i)
        while fail:
            try:
                ings = get_ings_map(batch)
                print(len(ings["ingredients"]))
                for ing in ings["ingredients"]:
                    ing_map[ing["name"]] = ing

                fail = False
                batch = []
            except KeyboardInterrupt:
                raise KeyboardInterrupt
            except Exception as e:
                print(e)
        if (i % 500) > 490:
            filename = "ing_mappings_full.pkl"
            with open(filename, "wb") as file:
                pickle.dump(ing_map, file)

if len(batch) > 0:
    fail = True
    while fail:
        try:
            ings = get_ings_map(batch)
            print(len(ings["ingredients"]))
            print(ings["ingredients"])
            for ing in ings["ingredients"]:
                ing_map[ing["name"]] = ing

            fail = False
            batch =  []
        except KeyboardInterrupt:
            raise KeyboardInterrupt
        except Exception as e:
            print(e)
            pass





filename = "ing_mappings_full.pkl"
with open(filename, "wb") as file:
    pickle.dump(ing_map, file)
