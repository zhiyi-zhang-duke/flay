from flask import Flask, render_template, request, redirect
import pymongo
from pymongo import MongoClient

import io
import csv
import json
import ast

app = Flask(__name__)
client = MongoClient("mongodb://db:27017")
db = client.projectDB
""" 
HELPER FUNCTIONS
"""

def loadDB():
    print("Initializing mongodb client")
    
    db_collection = db['recipe_data']
    #Uniqueness constraint for name, not necessary?
    # db_collection.createIndex( { "name": 1 }, { unique: true } )
    recipes = db_collection.recipes
    loaded_recipes_list = loadRecipes()
    for recipe in loaded_recipes_list:
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
        recipe['tags'] = data[5].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['n_steps'] = data[6].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['steps'] = data[7]
        recipe['description'] = data[8].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['ingredients'] = data[9]
        recipe['n_ingredients'] = data[10].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe_data.append(recipe)
    print(recipe_data)
    return recipe_data

"""
RESOURCES
"""

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/recipe/<id>")
def recipe(id):
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    result = recipes.find({'id': id})
    return render_template('recipe_content.html', result=result)    

@app.route("/results", methods=['GET','POST'])
def results():
    # Test request data
    # print(request)
    # request = {}
    # request.method = 'POST'
    # request.form = {'name': 'name', 'id': 'id', 'minutes': 'minutes', 'contributor_id': 'contributor_id', 'submitted': 'submitted', 'tags': 'tags', 'n_steps': 'nutrition', 'steps': 'n_steps', 'description': 'steps', 'ingredients': 'description', 'n_ingredients': 'ingredients'}, {'name': 'apple a day  milk shake', 'id': '5289', 'minutes': '0', 'contributor_id': '1533', 'submitted': '12/6/1999', 'tags': "['15-minutes-or-less', 'time-to-make', 'course', 'main-ingredient', 'cuisine', 'preparation', 'occasion', 'north-american', 'low-protein', '5-ingredients-or-less', 'beverages', 'fruit', 'american', 'easy', 'kid-friendly', 'dietary', 'low-sodium', 'shakes', 'low-calorie', 'low-in-something', 'apples', 'number-of-servings', 'presentation', 'served-cold', '3-steps-or-less']", 'n_steps': '[160.2, 10.0, 55.0, 3.0, 9.0, 20.0, 7.0]', 'steps': '4', 'description': "['combine ingredients in blender', 'cover and blend until smooth', 'sprinkle with ground cinnamon', 'makes about 2 cups']", 'ingredients': '', 'n_ingredients': "['milk', 'vanilla ice cream', 'frozen apple juice concentrate', 'apple']"}
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    if request.method == 'POST':
        print("---- Request -----")
        print(request.form)
        #Build mongodb regex
        recipe_searches = request.form['recipe'].split(" ")
        ingredient_searches = request.form['ingredient'].split(" ")
        queries = []
        for term in recipe_searches:
            collection_query = {}
            rgx = {}
            rgx['$regex']=term
            collection_query['name'] = rgx
            queries.append(collection_query)
        for term in ingredient_searches:
            collection_query = {}
            rgx = {}
            rgx['$regex']=term
            collection_query['n_ingredients'] = rgx
            queries.append(collection_query)
        print(queries)
        result = recipes.find( { "$or": queries } )
        return render_template('results_content.html', result=result)
    else:
        result = recipes.find({})
    return render_template('results_content.html', result=result)


if __name__ == '__main__':
    loadDB()
    app.run(debug=True,host='0.0.0.0')

#Useful things for reference
#Skipping parsing of post request for now
#flay   | ---- Request -----
#flay   | ImmutableMultiDict([('recipe', 'Chili'), ('ingredient', 'Tomatoes')])
#db.inventory.find( { item: { $in: [ /j/, /p/ ] } } )
#db.inventory.find( { $or: [ { status: "A" }, { qty: { $lt: 30 } } ] } )
#db.inventory.find( $or: [ { item: {"$regex" : "p"} }, { item: {"$regex" : "j"} } ] )
#db.inventory.find( { $or: [ {"": { "$regex": "A" }}, {"ingredient": { "$regex": "Tomatoes" }} ] } )
#db.inventory.find( $or: [ { item: {"$regex" : "p"} }, { item: {"$regex" : "j"} } ] )
#db.inventory.find( { $or: [ { item: {"$regex" : "p"} }, { item: {"$regex" : "j"} } ] } )
# 
# recipes.find( { "$or": [{'recipe': {'$regex': 'Chili'}}, {'ingredient': {'$regex': 'Tomatoes'}}] } )