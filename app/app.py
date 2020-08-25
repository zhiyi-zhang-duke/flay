from flask import Flask, render_template, request, redirect
import pymongo
from pymongo import MongoClient
from progress.bar import Bar

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
    recipes = db_collection.recipes
    loaded_recipes_list = loadRecipes()
    bar = Bar('Processing', max=len(loaded_recipes_list))
    for recipe in loaded_recipes_list:
        #Old Insert
        recipes.insert_one(recipe)
        bar.next()
    bar.finish()
    print("Database loaded successfully!")

def loadRecipes():
    #To do: Get measurements for ingredients into recipe content page    
    recipe_data = []

    #Load recipes
    csv_file = "./recipes_medium.csv"
    rows = io.open(csv_file, "r", encoding="utf-8")
    reader = csv.reader(rows)
    next(reader, None) #skip the header
    
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
        
    # print(recipe_data)
    return recipe_data

"""
RESOURCES
"""

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/about")
def about():
    return render_template('about.html')    

@app.route("/recipe/<id>")
def recipe(id):
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    result = recipes.find({'id': id})
    return render_template('recipe_content.html', result=result)    

@app.route("/results", methods=['GET','POST'])
def results():
    #To do: Results page needs to preserve query for paginated content    
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    if request.method == 'POST':
        print("---- Request -----")
        print(request.form)
        #Build mongodb regex
        recipe_searches = request.form['recipe'].split(",")
        ingredient_searches = request.form['ingredient'].split(",")
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
        result = recipes.find( { "$and": queries } ).limit(100)
        return render_template('results_content.html', result=result, skip=0)
    else:
        result = recipes.find({})
    return render_template('results_content.html', result=result, skip=0)

@app.route("/all/<skip>", methods=['GET','POST'])
def all(skip):
    skip = int(skip)
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    result = recipes.find({}).skip(skip).limit(100)
    return render_template('results_content.html', result=result, skip=skip)


if __name__ == '__main__':
    loadDB()
    app.run(debug=True,host='0.0.0.0')
    # app.run(host='0.0.0.0')

#Useful things for reference
#Skipping parsing of post request for now
#flay   | ---- Request -----
#flay   | ImmutableMultiDict([('recipe', 'Chili'), ('ingredient', 'Tomatoes')])
#db.inventory.find( { item: { $in: [ /j/, /p/ ] } } )
#db.inventory.find( $or: [ { item: {"$regex" : "p"} }, { item: {"$regex" : "j"} } ] )
#db.inventory.find( { $or: [ { item: {"$regex" : "p"} }, { item: {"$regex" : "j"} } ] } )
# 
# recipes.find( { "$and": [{'recipe': {'$regex': 'Chili'}}, {'ingredient': {'$regex': 'Tomatoes'}}] } )