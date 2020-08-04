#coding: utf-8
from flask import Flask, render_template
import pymongo
from pymongo import MongoClient

import io
import csv
import json

app = Flask(__name__)

""" 
HELPER FUNCTIONS
"""

def loadDB():
    print("Initializing mongodb client")
    client = MongoClient("mongodb://db:27017")
    db = client.projectDB
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    for recipe in loadRecipes():
        recipes.insert_one(recipe)
    print("Database loaded successfully!")

def loadRecipes():
    recipe_data = []

    #Load recipes
    csv_file = "./recipes_short.csv"
    rows = io.open(csv_file, "r", encoding="utf-8")
    reader = csv.reader(rows)
    for data in reader:
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
    return recipe_data

"""
RESOURCES
"""

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/test")
def testRoute():
    loadDB()
    return render_template('index.html')

if __name__ == '__main__':
    #loadDB()
    app.run(debug=True,host='0.0.0.0')

from app import routes