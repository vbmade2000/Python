# This file contains functions related to parsing data in Schema.org format.
# You can find related information and specifications on http://www.schema.org/Recipe

import microdata
import urllib
from recipe import Recipe

# Function to get Schema.org format data items from html data
def parseSchemaOrgData(htmldata, url):
	'''This function gets data embeded using Schema.org in <htmldata> and iterate through
	   each item and creates a list of Recipe objects containing these grabbed items.
	   It uses microdata library.	
	'''	
	print "Entered into parseSchemaOrgData() function"
	print "Parsing format Schema.org"
	retrivedItems = [] # List to hold retrieved items
	appendToList = retrivedItems.append
	if(len(htmldata)<=0):
		return []
	items = microdata.get_items(htmldata)
	if items and len(items)>0:
		
		for item in items:
			r = Recipe('','')
			r.link = str(url)
			r.name = item.name
			
			# Validation for description
			if item.description and len(item.description) >0:
				r.description = item.description
			
			# Validation for image
			if item.image and len(str(item.image)) >0:
				r.image = str(item.image)
				
			# Validation for prepTime
			if item.prepTime and len(item.prepTime) >0:
				r.prepTime = item.prepTime
			
			# Validation for cookTime
			if item.cookTime and len(item.cookTime) >0:
				r.cookTime = item.cookTime
				
			# Validation for recipeYield
			if item.recipeYield and len(item.recipeYield) >0:
				r.servings = item.recipeYield
				
			### Implemented specially for case insensitivity issue faced by client. 
			# Caution : This solution can cause problem in parsing in future	
			# Should be implemented in main python library
			if len(r.servings) == 0:
				if item.recipeyield and len(item.recipeyield) >0:
					r.servings = item.recipeyield	
			
			# Validation for ingredients
			if item.get_all('ingredients')and len(item.get_all('ingredients')) >0:
				r.ingredients = item.get_all('ingredients')
			
			# Validation for preparation
			if item.get_all('recipeInstructions') and len(item.get_all('recipeInstructions')) >0:
				r.preparation = item.get_all('recipeInstructions')
			
			### Implemented specially for case insensitivity issue faced by client
			# Should be implemented in html5lib python library
			if len(r.preparation) == 0:
				if item.get_all('recipeinstructions') and len(item.get_all('recipeinstructions')) >0:
					r.preparation = item.get_all('recipeinstructions')
						 
			# Validation for calories
			if item.nutrition:
				if item.nutrition.calories and len(item.nutrition.calories) >0:
					r.calories = item.nutrition.calories
			
			# Validation for fat
			if item.nutrition:
				if item.nutrition.fatContent and len(item.nutrition.fatContent) >0:
					r.fat = item.nutrition.fatContent
				
			# Validation for saturatedFat
			if item.nutrition:
				if item.nutrition.saturatedFatContent and len(item.nutrition.saturatedFatContent) >0:
					r.saturatedFat = item.nutrition.saturatedFatContent
			
			# Validation for salt
			if item.nutrition:
				if item.nutrition.sodiumContent and len(item.nutrition.sodiumContent) >0:
					r.salt = item.nutrition.sodiumContent
			
			# Validation for sugar
			if item.nutrition:
				if item.nutrition.sugarContent and len(item.nutrition.sugarContent) >0:
					r.sugar = item.nutrition.sugarContent
				
			# Validation for categories
			if item.nutrition:
				if item.recipeCategory and len(item.recipeCategory) >0:
					r.categories = item.recipeCategory
				
			# NOTE : Ratings, Tags and Keywords properties are not supported by standard 
			#        specifications of Schema.org/Recipe. Check out site http://www.schema.org/Recipe
			
			appendToList(r)	
			
	return retrivedItems			


# Testing of parser for Schema.org/Recipe format

# Sample Test Urls
# http://www.food.com/recipe/breakfast-potato-skins-489054
# http://www.bbcgoodfood.com/recipes/1304/15minute-chicken-pasta

#l = parseSchemaOrgData(urllib.urlopen('http://www.bbcgoodfood.com/recipes/1304/15minute-chicken-pasta').read(), '')
#for i in l:
#	print "Name : " + i.name
#	print "Deascription : " + i.description
#	print "Image :" + i.image
#	print "PrepTime : " + i.prepTime
#	print "CookTime : " + i.cookTime
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
#	print "Categories : " + i.categories
	
