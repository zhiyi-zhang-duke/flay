import pymongo
from pymongo import MongoClient

import io
import csv
import json


def loadDB():
	print("Initializing mongodb client")
	client = MongoClient("mongodb://127.0.0.1:27017")
	db = client['recipe_data']
	recipes = db.recipes
	print("Loading recipes...")
	for recipe in loadRecipes():
		recipes.insert_one(recipe)
	#recipes.insert_one(loadRecipes())
	print("Database loaded successfully!")

def loadRecipes():
	recipe_data = []

	#Load recipes
	csv_file = "./recipes_short.csv"
	rows = io.open(csv_file, "r", encoding="utf-8")
	reader = csv.reader(rows)
	for row in reader:
		#print(row)
		data = row
		#data = row.split("\t")
		recipe = {}
		recipe['name'] = data[0]
		recipe['id'] = data[1]
		recipe['minutes'] = data[2]
		recipe['contributor_id'] = data[3]
		recipe['submitted'] = data[4]
		recipe['tags'] = data[5]
		recipe['n_steps'] = data[6]
		recipe['steps'] = data[7]
		recipe['description'] = data[8]
		recipe['ingredients'] = data[9]
		recipe['n_ingredients'] = data[10]
		recipe_data.append(recipe)
	print(recipe_data)
	# return json.dumps(recipe_data)
	return recipe_data

loadDB()