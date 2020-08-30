from flask import Flask, session, render_template, request, redirect
import pymongo
from pymongo import MongoClient
from progress.bar import Bar
from bson.objectid import ObjectId
#Serialization
import pickle

import io
import csv
import json
import ast

app = Flask(__name__)
client = MongoClient("mongodb://db:27017")
db = client.projectDB
app.secret_key = 'flay'

""" 
HELPER FUNCTIONS
"""

def loadDB():
    print("Initializing mongodb client")
    db_collection = db['recipe_data']
    #Uniqueness constraint for name, not necessary?
    recipes = db_collection.recipes

    #Insert woks of life data
    file_data = loadWOLRecipes()
    print("Woks of life data size:")
    print(len(file_data))
    if isinstance(file_data, list):
        print("Attempting insert...")
        recipes.insert_many(file_data)
    print("Database loaded successfully!")

    #Insert kaggle dataset
    loaded_recipes_list = loadKaggleRecipes()
    bar = Bar('Processing', max=len(loaded_recipes_list))
    for recipe in loaded_recipes_list:
        recipes.insert_one(recipe)
        bar.next()
    bar.finish()

#Integrating woks of life recipes from flay-scrapy project
def loadWOLRecipes():
    with open('wol_recipes1.json') as file:
        file_data = json.load(file)
    return file_data

def loadKaggleRecipes():
    #To do: Add nutrition information formatting into recipe page
    recipe_data = []

    #Load recipes
    csv_file = "./recipes_medium.csv"
    rows = io.open(csv_file, "r", encoding="utf-8")
    reader = csv.reader(rows)
    next(reader, None) #skip the header
    
    for data in reader:
        recipe = {}
        recipe['name'] = data[0].title()
        # recipe['id'] = data[1]
        recipe['minutes'] = data[2]
        recipe['contributor'] = ""
        recipe['contributor_id'] = data[3]
        recipe['submitted'] = data[4]
        recipe['tags'] = data[5].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['nutrition'] = data[6].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['n_steps'] = data[7]
        recipe['steps'] = data[8].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['description'] = data[9]
        recipe['ingredients'] = data[10].lstrip('[').rstrip(']').replace("'", "").split(',')
        recipe['n_ingredients'] = data[11]
        recipe['image'] = ""
        recipe['recipeURL'] = ""
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
    result = recipes.find_one({'_id': ObjectId(id)})
    return render_template('recipe_content.html', result=result)    

@app.route("/results/<skip>", methods=['GET','POST'])
def results(skip):
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    skip = int(skip)
    if request.method == 'POST':
        print("---- Request -----")
        print(request.form)
        #Build mongodb regex
        recipe_searches = request.form['recipe'].split(",")
        ingredient_searches = request.form['ingredient'].split(",")
        queries = []
        if recipe_searches:
            for term in recipe_searches:
                collection_query = {}
                rgx = {}
                rgx['$regex']=term
                collection_query['name'] = rgx
                queries.append(collection_query)
        if ingredient_searches:
            for term in ingredient_searches:
                collection_query = {}
                rgx = {}
                rgx['$regex']=term
                collection_query['ingredients'] = rgx
                queries.append(collection_query)
        #Save last query
        session['lastQuery'] = queries
        print("Last query was ", session['lastQuery'])
        # print(queries)
        result = recipes.find( { "$and": queries } ).limit(100)
        return render_template('results_content.html', result=result, skip=skip, mode="results")
    else:
        queries = session['lastQuery']
        result = recipes.find( { "$and": queries } ).skip(skip).limit(100)
        #Paginate results
    return render_template('results_content.html', result=result, skip=skip, mode="results")

@app.route("/all/<skip>", methods=['GET','POST'])
def all(skip):
    skip = int(skip)
    db_collection = db['recipe_data']
    db_collection.find().sort( [('name' , -1)])
    recipes = db_collection.recipes
    result = recipes.find({}).skip(skip).limit(100)
    print(result.count())
    return render_template('results_content.html', result=result, skip=skip, mode="all")

#A useful route for checking the data of a recipe
@app.route("/recipe/debug/<id>")
def recipeDebug(id):
    db_collection = db['recipe_data']
    recipes = db_collection.recipes
    result = recipes.find_one({'_id': ObjectId(id)})
    return render_template('test_print.html', result=result)   

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