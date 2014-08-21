import rdflib
import urllib
from rdflib.namespace import RDF
from rdflib import *
from recipe import Recipe

#def getRecipeData():
	#v = Namespace("http://rdf.data-vocabulary.org/#")
	#f = open(r'D:\Malhar Data\TestGround\test.html')
	#rdfdata = f.read()

	#f.close()
	#g=rdflib.Graph()
	#g.parse(data=rdfdata, format='rdfa1.1', media_type='text/html')

	#for recipe in g.subjects(RDF.type, v.Recipe):
	#	print "Name : " + g.value(recipe, v.name) ##
    #	print "Description : " + g.value(recipe, v.summary) ###
	#	print "PrepTime : " + g.value(recipe, v.prepTime) ###
	#	print "CookTime : " + g.value(recipe, v.cookTime) ##
	#	print "Sugar : " + str(g.value(recipe, v.sugar))
	#	print "Photo : " + str(g.value(recipe, v.photo)) ##
	#	print "Instructions : " + str(g.value(recipe, v.instructions)) ##
	#	print "Ingredients:" ##
	#	for ingredient in g.objects(recipe, v.ingredient): ##
	#		print "- %s: %s" % (g.value(ingredient, v.name), g.value(ingredient, v.amount))
	#	print "Nutritions:"
	#	for nutrition in g.objects(recipe, v.nutrition):
	#		print "- Calories : %s" % (g.value(nutrition,v.calories))
	#		print "- Fat : %s" % (g.value(nutrition,v.fat))
	#		print "- Saturated Fat : %s" % (g.value(nutrition,v.saturatedFat))
		
			
			
		

def parseRdfData(htmldata, url):
	'''This function gets data embeded using format http://rdf.data-vocabulary.org/# in <htmldata> and iterate through
	   each item and creates a list of Recipe objects containing these grabbed items.
	   It uses rdflib library.	
	'''	
	print "Entered into parseRdfData() function"
	print "Parsing format RDFa"
	v = Namespace("http://rdf.data-vocabulary.org/#")
	rdfdata = htmldata
	g=rdflib.Graph()
	g.parse(data=rdfdata, format='rdfa1.1', media_type='text/html')
	
	retrivedItems = [] # List to hold retrieved items
	appendToList = retrivedItems.append
	if(len(htmldata)<=0):
		return []

	for recipe in g.subjects(RDF.type, v.Recipe):	
		r = Recipe('','')
		r.link = str(url)
		r.name = g.value(recipe, v.name)
		
		# Validation for description
		if  g.value(recipe, v.summary) and len( g.value(recipe, v.summary)) >0:
			r.description = g.value(recipe, v.summary)
		
		# Validation for photo
		if g.value(recipe, v.photo) and len(str(g.value(recipe, v.photo))) >0:
			r.image = str(g.value(recipe, v.photo))
			
		# Validation for prepTime
		if g.value(recipe, v.prepTime) and len(g.value(recipe, v.prepTime)) >0:
			r.prepTime = g.value(recipe, v.prepTime)
		
		# Validation for cookTime
		if g.value(recipe, v.cookTime) and len(str(g.value(recipe, v.cookTime))) >0:
			r.cookTime = str(g.value(recipe, v.cookTime))
		
		# Validation for sugar
		if g.value(recipe, v.sugar) and len(str(g.value(recipe, v.sugar))) >0:
			r.sugar = str(g.value(recipe, v.sugar))
		
		# Validation for tags
		if g.value(recipe, v.tag) and len(str(g.value(recipe, v.tag))) >0:
			r.tag = str(g.value(recipe, v.tag))
			
		# Validation for Category
		if g.value(recipe, v.recipeType) and len(str(g.value(recipe, v.recipeType))) >0:
			r.categories = str(g.value(recipe, v.recipeType))
		
		# Validation for ingredients
		if g.objects(recipe, v.ingredient):
			append = r.ingredients.append
			for ingredient in g.objects(recipe, v.ingredient):
				print "#########-->>>>>>>>>>>:" + g.value(ingredient, v.name)
				append(str(g.value(ingredient, v.name)) + " : " + str(g.value(ingredient, v.amount)))
		
		# Validation for instructions
		if str(g.value(recipe, v.instructions)) and len(str(g.value(recipe, v.instructions))) >0:
			r.preparation.append(str(g.value(recipe, v.instructions)))
					
		# Validation for nutrition
		if g.objects(recipe, v.nutrition):
			for nutrition in g.objects(recipe, v.nutrition):
				# Validation for calories
				if g.value(nutrition,v.calories) and len(str(g.value(nutrition,v.calories)))>0:
					r.calories = str(g.value(nutrition,v.calories))
				# Validation for fat
				if g.value(nutrition,v.fat) and len(str(g.value(nutrition,v.fat)))>0:
					r.fat = g.value(nutrition,v.fat)
				# Validation for saturatedFat
				if g.value(nutrition,v.saturatedFat)and len(str(g.value(nutrition,v.saturatedFat)))>0:
					r.saturatedFat = g.value(nutrition,v.saturatedFat)
		
		# Validation for yield
		# NOTE : Due to Python keyword conflict with specification keyword "yield",
		#		 this field can not be implemented  	
		
		# NOTE : Salt, Ratings and Keywords properties are not supported by standard 
		#        specifications of Schema.org/Recipe. Check out site http://rdf.data-vocabulary.org/#
		
		appendToList(r)	
			
	return retrivedItems			
	
	
 
#f = open(r'D:\Malhar Data\TestGround\test.html')
#rdfdata = f.read()
#f.close() 

#Testing of parser for http://rdf.data-vocabulary.org/# format
#l = parseRdfData(rdfdata,r'D:\Malhar Data\TestGround\test.html')
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
	