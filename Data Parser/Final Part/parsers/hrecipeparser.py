# This file contains functions related to parsing data in microformat hRecipe format.
# You can find more information and specifications on http://microformats.org/wiki/hrecipe

from BeautifulSoup import BeautifulSoup
import urllib
from recipe import Recipe
import types


# Function to grab hRecipe data from given url
# Developed by : Ben Osment
# Original file : hrecipe_parse.py
def review_scrape(htmldata):
    """ Given a htmldata, find all hRecipes listed and return a dictionary of
        the attributes"""
    try:
        soup = BeautifulSoup(htmldata)
    except Exception as e:
        print "Failed to parse", url
        sys.exit()

    hrecipes = soup.findAll(True, 'hrecipe')
   
    return [soup_to_dict(hrecipe,htmldata) for hrecipe in hrecipes]

# Function to create dictionary from grabbed data
# Developed by : Ben Osment
# Original file : hrecipe_parse.py	
def soup_to_dict(hrecipe,htmldata):
    d = {}
    # only fn and ingredient are mandatory, all other fields
    # are optional
    d['fn'] = hrecipe.find(True, 'fn').text
    # ingredients (multiple)
    ingredients = hrecipe.findAll(True, 'ingredient')
    i = []
    for ingredient in ingredients:
        q = ingredient.find(True, 'quantity')
        u = ingredient.find(True, 'unit')
        n = ingredient.find(True, 'name')
        if q and u and n:
            i.append('%s %s %s' % (q.text, u.text, n.text))
        else:
            i.append(ingredient.text)
    d['ingredient'] = i

    # TODO -- this could probably be refactored
    # yield
    _yield = hrecipe.find(True, 'yield')
    if _yield:
        d['yield'] = _yield.text
    # instructions (multiple)
    instructions = hrecipe.findAll('span', 'instructions')
    if instructions:
        d['instructions'] = [instruction.text for instruction in instructions]
    # duration
    duration = hrecipe.find(True, 'duration')
    if duration:
        d['duration'] = duration.text
    
	# summary
    summary = hrecipe.find(True, 'summary')
    if summary:
        d['summary'] = summary.text
	
	# photo
	# Implemented
	# This function can still be improved
	photosoup = BeautifulSoup(htmldata)
	phototag = photosoup.find('img',{'class':'photo'})
	if phototag:
		srcvalue = [item[1] for item in phototag.attrs if item[0]=='src']
		if srcvalue:
			d['photo'] = str(srcvalue[0])
    
    # author
    author = hrecipe.find(True, 'author')
    if author:
        d['author'] = author.text
    # published
    published = hrecipe.find(True, 'published')
    if published:
        d['published'] = published.text
    # nutrition
    nutrition = hrecipe.find(True, 'nutrition')
    if nutrition:
        d['nutrition'] = nutrition.text
    # tag (multiple)
    tags = hrecipe.findAll(True, 'tag')
    if tags:
        d['tag'] = [tag.text for tag in tags]

    return d


# Function to get hrecipe format data items from html data
def parsehRecipeData(htmldata, url):
	'''This function calls function <review_scrape> and passed <htmldata> to it.
	   It uses BeautifulSoup library.
	'''	
	print "Entered into parsehRecipeData() function"
	print "Parsing format hrecipe"
	retrivedItems = [] # List to hold retrieved items
	appendToList = retrivedItems.append
	if(len(htmldata)<=0):
		return []
	
	hrecipes = review_scrape(htmldata)
	if hrecipes and len(hrecipes)>0:
		for recipe in hrecipes:
			
			r = Recipe('','')
			r.link = str(url)
			r.name = recipe['fn']
			
			# Validation for description
			summary = recipe.get('summary','None')
			if summary != "None":
				r.description = summary

			# Validation for image
			photo = str(recipe.get('photo','None'))
			if photo != "None":
				r.image = photo
				
			# Validation for duration
			duration = str(recipe.get('duration','None'))
			if duration != "None":
				r.prepTime = duration
			
			# Validation for yield
			yields = str(recipe.get('yield','None'))
			if yields != "None":
				r.servings = yields
			
			# Validation for ingredient
			ingredient = recipe.get('ingredient',[])
			if ingredient != "None":
				r.ingredients = ingredient
				
			# Validation for instructions
			instructions = recipe.get('instructions','None')
			if instructions != "None":
				#r.preparation[0] = str(instructions)
				r.preparation.append(str(instructions))
			
			# NOTE : In hrecipe format nutrition is a text value where as Recipe class has multiple attrbutes.
			# 		 So nutrition part is not implemented
			# Validation for nutrition
			# nutrition = recipe.get('nutrition','None')
			# if nutrition != "None":
			#	r.ingredients[0] = nutrition
			
			appendToList(r)
	return retrivedItems 		



	
# Testing of parser for Schema.org/Recipe format
# Sample urls
# http://www.landolakes.com/recipe/643/caesar-chicken-pasta
# http://www.canadianliving.com/food/lemony_chicken_pasta.php
				
#l = parsehRecipeData(urllib.urlopen('http://allrecipes.co.uk/recipe/6115/spinach--mushroom-and-feta-quiche.aspx').read(), 'http://allrecipes.co.uk/recipe/6115/spinach--mushroom-and-feta-quiche.aspx')
#l = parsehRecipeData(urllib.urlopen('http://recipes.coles.com.au/recipes/2361/pesto-chicken-pasta').read(), '')



#for i in l:
#	print "Name : " + i.name
#	print "Description : " + i.description
#	print "Image :" + i.image
#	print "PrepTime : " + " Not implemented in specification"
#	print "CookTime : " + "Not implemented in specification"
#	print "Servings : " + i.servings
#	print "########################"
#	print "_________________" + str(len(i.ingredients))
#	print "Ingredients : " + str(i.ingredients)
#	print "########################"
#	print "_________________" + str(len(i.preparation))
#	print "Preparation : " + str(i.preparation)
#	print "########################"
#	print "Calories : " + i.calories
#	print "Saturated Fat : " + i.saturatedFat
#	print "Fat : " + i.fat
#	print "Salt : " + i.salt
#	print "Sugar : " + i.sugar
