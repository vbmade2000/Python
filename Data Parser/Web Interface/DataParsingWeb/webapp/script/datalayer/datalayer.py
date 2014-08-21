# This python script contains a class to deal with internals of database and insertion of data

import MySQLdb as mysql
import imp
import sys
from urlparse import urlparse
from os.path import splitext, basename
import re
import time
import urllib
import shutil # For filecopy operation
import Image # To resize image
import tempfile # To generate temporary file

try:
	recipe = imp.load_source('recipe', '../parsers/recipe.py')
except:
	#from parsers.recipe import Recipe
	from parsers import recipe




class DataManager():
	'''This class manages database operations such as connection to database,
		checking for existing recipe, insertion of new recipe etc.
		It uses MySQLdb library to connect with mysql database
	'''
	
	# Function to reverse a string
	def reverseString(self, strinput):
		return strinput[::-1]
	
	# This function extracts minutes from string like PT10
	def extractMinuteFromISOFormat(self, strinput):
		'''This function extracts minutes from ISO format duration value (Ex. PT10M) 
			return : Minutes extracted from string
		'''
		ret = ''
		strvalue = ''
		minutes = 0
		hours = 0
		
		strtemp = strinput.lower().strip()
		# Get location of t in entire string
		time_location = strtemp.find('t')
		# Fetch Time part of entire string
		strtime = strtemp[time_location:len(strtemp)]
		
		# Extract Minutes
		strvalue = ''
		minute_loc = strtime.find('m')
		if minute_loc > -1:
			minute_value = strtime[1:minute_loc].strip()
			if len(minute_value) > 0: # If minute is found
				
				count = int(minute_loc-1)
				# Extracting numeric values until found
				while count>=0:
					if strtime[count].isdigit():
						strvalue = strvalue + strtime[count]
					else:
						break
					count = count -1
		if len(strvalue.strip()) > 0:
			minutes = int(self.reverseString(strvalue))
		
		# Extract Hours
		strvalue = ''
		hour_loc = strtime.find('h')
		if hour_loc > -1:
			hour_value = strtime[1:hour_loc].strip()
			if len(hour_value) > 0: # If hour is found
				count = int(hour_loc-1)
				# Extracting numeric values until found
				while count>=0:
					if strtime[count].isdigit():
						strvalue = strvalue + strtime[count]
					else:
						break
					count = count -1
		if len(strvalue.strip()) > 0:
			hours = int(self.reverseString(strvalue))
			
		print "Minutes : " +  str(minutes)
		print "Hours : " +  str(hours)
		minutes = int(minutes)+ (int(hours) * 60)
		return minutes

	
	def __init__(self, host='localhost', user='root', password='', database='', port=3306, mappingdict = {}, imagepath='', imageresizepath=''):
		print "Data Manager instance initiated..."
		self.dbhost = host
		self.dbuser = user
		self.dbpassword = password
		self.db = database
		self.dbport = port
		self._connection = mysql.connect(self.dbhost, self.dbuser, self.dbpassword, self.db, self.dbport)
		self._cursor = self._connection.cursor()
		self._connection.autocommit(False)
		self._mappingdict = mappingdict
		self._image_file_path = imagepath # Path to store recipe image
		self._image_resize_path = imageresizepath # Path to store resized recipe image
		
	def getFilenameAndExtension(self, url):
		'''This function retrieves filename and extension from a given url
			It uses urlparse library
			Returns : Tuple containing (filename,extension)
		'''
		
		if url:
			disassembled = urlparse(url)
			filename, file_ext = splitext(basename(disassembled.path))
			return(filename, file_ext)
		else:
			return ('','')
		
	def insertNodeRevisionTableEntry(self, node_id, recipetitle):
		'''This function inserts entry in <node_revision> table
			Parameters : recipetitle - Title of recipe to be inserted
						 conn - Instance of MySQLdb.Cursor class to be used
						 node_id - Primary key of <node> table entry
			Returns : vid (integer) value(Primary key) of newly inserted node_revision record
		'''
		modified_title = mysql.escape_string(self.escape(recipetitle.strip().encode('UTF-8','ignore')))
		print "=> Entered into function insertNodeRevisionTableEntry"
		self._cursor.execute("INSERT INTO node_revision (nid, title, log, status) VALUES(%s, '%s', 'No Change', 0);" % (node_id, modified_title)) 
		self._cursor.execute("SELECT LAST_INSERT_ID()") # Get auto incremented Primary key of newly inserted row
		#self._connection.commit()
		results = self._cursor.fetchall()
		return results[0][0] # Return value of <vid> column of newly inserted record
		
	def getCurrrentUnixTimeStamp(self):
		'''Function to generate unix timestamp value from current date
			It uses <time> module.
			Returns the unix timestamp of current date
		'''
		return int(time.time())
		
	def extractDomainWithExtension(self, url):
		'''This function extracts name of domain and extension.
		   i.e from www.food.com it extracts food.com
		   It uses urlparse module.
		   Returns domain.extension
		'''
		if not url.startswith("http://"):
			url = "http://" + url
		parts = urlparse(url)
		return str(parts.netloc.lstrip("www."))	
	
	def insertNodeTableEntry(self, vid, recipetitle, link):
		'''This function inserts entry in <node> table.
			Parameters : vid - Primary key value of newly created record in <node_revision> table. It can be retrieved by calling 
								insertNodeRevisionTableEntry() function.
						 recipetitle - Title of the recipe to be inserted.
			Returns : nid (integer) value of newly inserted node record
		'''
		nid = 0 # Variable to hold primary key of newly inserted record in node table
		vid = 0
		count = self.getMaxVidFromNodeTable()
		if count is None:
			count = 1
		else:
			count = int(count) + 1
		modified_title = mysql.escape_string(self.escape(recipetitle.strip().encode('UTF-8','ignore')))
		print "->>>>>>>>Count" + str(count)
		print "=> Entered into function insertNodeTableEntry"
		website_domain = self.extractDomainWithExtension(link)
		print str(self._mappingdict)
		print "wesite_domain||||||||||||||||" + website_domain
		default_uid = self._mappingdict.get(self.extractDomainWithExtension('http://www.default.com'),'1')
		recipe_uid = self._mappingdict.get(website_domain, default_uid)
	
		self._cursor.execute("INSERT INTO node (vid, title, type, uid, language, created, changed, status) VALUES(%s, '%s', 'recipe', %s, 'und', '%s', '%s', 0);" % (count, modified_title, recipe_uid, self.getCurrrentUnixTimeStamp(), self.getCurrrentUnixTimeStamp())) 
		self._cursor.execute("SELECT LAST_INSERT_ID()") # Get auto incremented Primary key of newly inserted row 
		#self._connection.commit()
		results = self._cursor.fetchall()
		nid =  results[0][0]
		self._cursor.execute("UPDATE node SET vid = %s WHERE nid = %s;" % (nid, nid))
		 
		
		return  nid # Return value of <nid> column of newly inserted record

	def insertTaxonomyTablesEntry(self, category):
		'''This function inserts entry into <taxonomy_term_data> table.
			Parameters : category - Category of recipe. It's a simple text value.
			Returns : tid (integer) value of newly inserted Taxonomy record
		'''
		print "=> Entered into function insertTaxonomyTablesEntry"
		self._cursor.execute("INSERT INTO taxonomy_term_data (name) VALUES('%s');" % (category)) 
		self._cursor.execute("SELECT LAST_INSERT_ID()") # Get auto incremented Primary key of newly inserted row 
		self._connection.commit()
		results = self._cursor.fetchall()
		return results[0][0] # Return value of <tid> column of newly inserted record
	
	
	def getTempFile(self):
		'''Function to generate temporary file.
			It uses <tempfile> package.
			Returns file name of generated file
		'''	
		f = tempfile.NamedTemporaryFile(delete=False)
		f.close()
		return f.name
		
		
	def downloadImageFromURI(self, uri):
		'''Function to download image from given uri.
			Downloads and stores image at IMAGE_STORAGE_PATH in settings.py
			Returns path of locally stored image.		
		'''
		# Get file name from uri
		image_file_name = self.getFilenameAndExtension(uri)[0]
		# Get file extension from uri
		image_file_extension = self.getFilenameAndExtension(uri)[1].strip().lower()
		image_file = image_file_name + image_file_extension
		local_image_path = self._image_file_path + image_file
		local_image_path2 = self._image_resize_path + image_file
		
		# Read binary data from uri
		image_data = urllib.urlopen(uri).read()
	
		# Resize recipe image using Image module
		tempfilename = self.getTempFile()
		tempfile = open(tempfilename, "wb")
		tempfile.write(image_data)
		tempfile.close()
		
		orig_image = Image.open(tempfilename)
		
		# Resize original image using anti aliasing method for best results
		resized_image = orig_image.resize((250,250), Image.ANTIALIAS)
		resized_image.save(local_image_path)
		reszd_img = Image.open(local_image_path)
		reszd_img.save(local_image_path2)
		
		print "Images saved"
	
		# Create image file in main folder
		##imagefile = open(local_image_path,"wb")
		##imagefile.write(image_data)
		##imagefile.close()
		
		# Create image file in another folder
		##local_image_path2 = self._image_resize_path + image_file
		##imagefile = open(local_image_path2,"wb")
		##imagefile.write(image_data)
		##imagefile.close()		
		
		return local_image_path
		
	
	def insertImageTableEntry(self, filename, uri, filesize, filemime):
		'''This function insert entry into <file_managed> table.
			Parameters : filename - Name of the file with no path component
						 uri - URI to access the file. Either local or remote.
						 filesize - Size of file in bytes
			Returns : fid (integer) value of newly inserted image if inserted successfully, 0 otherwise
		'''
		print "=> Entered into function insertImageTableEntry"
		
		if not len(uri.strip())==0:
			image_file_name= self.downloadImageFromURI(uri)
			self._cursor.execute("INSERT INTO file_managed (filename, uri, filemime, filesize, status) VALUES('%s', '%s', '%s', '%s', 1);" % (filename, mysql.escape_string(image_file_name), filemime, filesize)) 
			self._cursor.execute("SELECT LAST_INSERT_ID()") # Get auto incremented Primary key of newly inserted row 
			self._connection.commit()
			results = self._cursor.fetchall()
			return results[0][0] # Return value of <fid> column of newly inserted record
		else: # Return 0 if uri is blank
			print "Recipe image not found"
			return 0
		
		
	
	def extractNoFromText(self, text):
		'''Function to extract number from text using regular expression
			Returns a list of numbers extracted from text.
		'''
		return re.findall('\d*.\d+', text)
		
	def insertRecipeTableEntry(self, nid, title, source, yields, description, preptime, cooktime, calories, fat, saturates, salt, sugar, recipe_image, categories = ''):
		'''This function inserts recipe into the database
			Parameters : nid - Primary key value of newly created record in <node> table. It can be retrieved by calling
							   insertNodeTableEntry() function.
						 title - Title of the recipe
						 source - Link from which recipe is taken
						 yields - No of servings
						 description - Description of recipe
						 preptime - Preparation time for recipe
						 cooktime - Cooking time for recipe
						 calories - Calories contained by recipe
						 fat - Fat content in recipe
						 saturates - Saturated Fat contents in recipe
						 salt - Salt contents in recipe
						 Sugar - Sugar contents in recipe
						 recipe_image - Unique url of recipe
						 categories = tid of taxonomies
			Returns : nid - Primary key of newly inserted recipe 			 
		'''
		print "Entered into datalayer.insertRecipeTableEntry() function"
		modified_preptime = self.extractMinuteFromISOFormat(preptime.encode('UTF-8','ignore'))
		modified_cooktime = self.extractMinuteFromISOFormat(cooktime.encode('UTF-8','ignore'))
		modified_description = self.escape(description.strip().encode('UTF-8','ignore'))
		modified_title = mysql.escape_string(self.escape(title.strip().encode('UTF-8','ignore')))
		modified_source = self.escape(source.strip().encode('UTF-8','ignore'))
		modified_yield = self.extractNoFromText(yields)
		
		# Processing sugar value 
		extracted_sugar = self.extractNoFromText(sugar) # Extract float no from text
		if len(extracted_sugar) > 0:
			modified_sugar = float(extracted_sugar[0])
		else:
			modified_sugar = ''
		
		# Processing saturates value 
		extracted_saturates = self.extractNoFromText(saturates) # Extract float no from text
		if len(extracted_saturates) > 0:
			modified_saturates = float(extracted_saturates[0])
		else:
			modified_saturates = ''
		
		# Processing fat value
		extracted_fat = self.extractNoFromText(fat) # Extract float no from text
		if len(extracted_fat) > 0:
			modified_fat = float(extracted_fat[0])
		else:
			modified_fat = ''
				
		# Processing salt value
		extracted_salt = self.extractNoFromText(salt) # Extract float no from text
		if len(extracted_salt) > 0:
			modified_salt = float(extracted_salt[0]) / 1000.0 # Salt value comes in mg. So convert it to gram.
			modified_salt = "%.2f" % modified_salt # Round off the value of salt to two nos
		else:
			modified_salt = ''
		
		# Prepare link_description column of recipe table. 
		# It should be domain name of source url of recipe without "www".
		link_description = urlparse(source).netloc.lstrip("www.")
		print "\n\n"
		print "&&&&&&&&&&&&&&& : Link Description " + link_description
		
		
		print "===>>+>+>+>+>+>+>+>" + modified_title
		
		recipe_insert_query = "INSERT INTO recipe (nid, title, source, yield, description, preptime, cooktime, calories, fat, saturates, salt, sugars, recipe_image, categories, difficulty_level, link_description) VALUES('%s', '%s', '%s', '%s', '%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', 'Moderate', '%s');" % (nid, modified_title, modified_source, yields, modified_description, modified_preptime, modified_cooktime, calories.encode('UTF-8','ignore'), modified_fat, modified_saturates, modified_salt, modified_sugar, recipe_image, categories.encode('UTF-8','ignore'), link_description )
		#self._cursor.execute("INSERT INTO recipe (title, source, yield, description, preptime, cooktime, calories, fat, saturates, salt, sugars, recipe_image, categories) VALUES('%s','%s','%s','%s',%s,%s,'%s','%s','%s','%s','%s','%s','%s');" % (title.encode('UTF-8','ignore'), source.encode('UTF-8','ignore'), yields.encode('UTF-8','ignore'), modified_description.encode('UTF-8','ignore'), modified_preptime, modified_cooktime, calories.encode('UTF-8','ignore'), fat.encode('UTF-8','ignore'), saturates.encode('UTF-8','ignore'), salt.encode('UTF-8','ignore'), sugar.encode('UTF-8','ignore'), recipe_image, categories.encode('UTF-8','ignore') )) 
		self._cursor.execute(recipe_insert_query)
		self._cursor.execute("SELECT LAST_INSERT_ID();") # Get auto incremented Primary key of newly inserted row 
		#self._connection.commit()
		results = self._cursor.fetchall()
		return results[0][0] # Return value of <nid> column of newly inserted record
	
	def getMaxVidFromNodeTable(self):
		print "getMaxVidFromNodeTable() executed"
		self._cursor.execute("SELECT MAX(vid) FROM node_revision;")
		count = self._cursor.fetchone()
		print "->>>>>>>CountID : " + str(count[0])
		print "getMaxVidFromNodeTable() completed"
		return count[0]
	
	def escape(self, t):
		"""HTML-escape the text in `t`."""
		return (t
			.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
			.replace("'", "&#39;").replace('"', "&quot;")
			)	
	def insertRecipe(self, recipe):
		'''This function inserts recipe into the database
			Parameters : recipe - Instance of Recipe class to be inserted
			Returns : nid (integer) value of newly inserted record		
		'''
		print "insertRecipe() executed----"		
		# Get file name from uri
		image_file_name = self.getFilenameAndExtension(recipe.image)[0]
		# Get file extension from uri
		image_file_extension = self.getFilenameAndExtension(recipe.image)[1].strip().lower()
		image_file = image_file_name + image_file_extension
		
		# Decide mimte_type according to extension
		image_mime_type = ""
		if image_file_extension.strip() == '.gif':
			image_mime_type = 'image/gif'
		if image_file_extension.strip() == '.jpeg':
			image_mime_type = 'image/jpeg'
		if image_file_extension == '.pjpeg':
			image_mime_type = 'image/pjpeg'
		if image_file_extension == '.png':
			image_mime_type = 'image/png'
		if image_file_extension == '.svg':
			image_mime_type = 'image/svg'
		if image_file_extension == '.tiff':
			image_mime_type = 'image/tiff'
		if image_file_extension == '.jpg':
			image_mime_type = 'image/jpeg'
			
		

		try:
			
			vid = -1
			node_id = -1
			taxonomy_id = -1
			image_file_id = -1
   			recipe_id = -1
			self._cursor.execute('START TRANSACTION;')
			print '#####################--Transaction Started--#########################'
			
			node_id = self.insertNodeTableEntry(vid, recipe.name, recipe.link) # Create Node record
			print '#####################--Node Created (%s)--#########################' % ("Primary key of node table :" + str(node_id))
			
			vid = self.insertNodeRevisionTableEntry(node_id, recipe.name) # Create NodeRevision record
			print '#####################--NodeRevision Created (%s)--#########################' % ("Primary key of node_revision table :"  +str(vid))
			
			taxonomy_id = self.insertTaxonomyTablesEntry(recipe.categories) # Create Taxonomy Record
			print '#####################--Taxonomy Created (%s)--#########################' % (str(taxonomy_id))
			image_file_id = self.insertImageTableEntry(image_file,recipe.image,0,image_mime_type) # Create Image record
			print '#####################--Image Created (%s)--#########################' % (str(image_file_id))
			recipe_id = self.insertRecipeTableEntry(node_id, recipe.name, recipe.link, recipe.servings, recipe.description, recipe.prepTime, recipe.cookTime, recipe.calories, recipe.fat, recipe.saturatedFat, recipe.salt, recipe.sugar, image_file_id, str(taxonomy_id )) # Create Recipe Record 
			print '#####################--Recipe Created (%s)--#########################' % (str(recipe_id))
			self.insertPreparationTableEntry(node_id, recipe.link, recipe.preparation )
			print '#####################--Preparation Created --#########################'
			self.insertRecipeIngredientsTableEntry(node_id, recipe.ingredients)
			print '#####################--Ingredients Created --#########################'
			self._connection.commit()
			print "#####################--Commit code executed --########################"
		except mysql.Error as err:
			self._cursor.execute('ROLLBACK;')
			
			# Check if entry in node_revision table is created
			if vid != -1:
				print "vid++++++" + str(vid)
				self._cursor.execute("DELETE FROM node_revision WHERE vid = %s;" % (vid)) 
				self._connection.commit()
			else:
				print "Node Revision is not created"
				
			# Check if entry in node table is created				
			if node_id != -1:
				print "node_id++++++" + str(node_id)
				self._cursor.execute("DELETE FROM node WHERE nid = %s;" % (node_id)) 
				self._connection.commit()
			else:
				print "Node is not created"	
				
			# Check if entry in taxonomy_term_data table is created					
			if taxonomy_id != -1:
				print "taxonomy_id++++++" + str(taxonomy_id)
				self._cursor.execute("DELETE FROM taxonomy_term_data WHERE tid = %s;" % (taxonomy_id)) 
				self._connection.commit()
			else:
				print "Taxonomy is not created"	
				
			# Check if entry in file_managed table is created						
			if image_file_id != -1:
				print "image_file_id++++++" + str(image_file_id)
				self._cursor.execute("DELETE FROM file_managed WHERE fid = %s;" % (image_file_id)) 
				self._connection.commit()
			else:
				print "Image is not created"	
				
			# Check if entry in recipe table is created						
			if recipe_id != -1:
				print "recipe_id++++++" + str(recipe_id)
				self._cursor.execute("DELETE FROM node_revision WHERE nid = %s;" % (recipe_id)) 
				self._connection.commit()
			else:
				print "Recipe is not created"	
			
			# Check if entries in recipe_ingredients table is created		
			if recipe_id != -1:
				print "recipe_id++++++" + str(recipe_id)
				self._cursor.execute("DELETE FROM recipe_ingredients WHERE nid = %s;" % (recipe_id)) 
				self._connection.commit()
			else:
				print "Recipe Ingredients are not created"	
			
			# Check if entries in recipe_preparation_method table is created	
			if recipe_id != -1:
				print "recipe_id++++++" + str(recipe_id)
				self._cursor.execute("DELETE FROM recipe_preparation_method WHERE nid = %s;" % (recipe_id)) 
				self._connection.commit()
			else:
				print "Recipe Preparations are not created"				
			print("Something went wrong: " + str(err))

		
	def insertRecipeIngredientsTableEntry(self, nid, ingredients = []):
		'''This function inserts entry into <recipe_ingredients> table.
			Parameters : nid - Primary key value of newly created record in <node> table. It can be retrieved by calling
								insertNodeTableEntry() function.
						 ingredients - List of ingredients to be inserted.
			Returns : Nothing
		'''
		print "=> Entered into function insertRecipeIngredientsTableEntry"
		if len(ingredients) > 0:
			for ingredient in ingredients:
				self._cursor.execute("INSERT INTO recipe_ingredients (nid, ri_title) VALUES(%s,'%s');" % (nid, mysql.escape_string(ingredient.strip().encode('utf-8'))))
				#self._connection.commit()	
	
	
	
	def insertPreparationTableEntry(self, nid, link, preparationSteps = []):
		'''This function inserts entry into <recipe_preparation_method> table.
			Parameters : nid - Primary key value of newly created record in <node> table. It can be retrieved by calling 
								insertNodeTableEntry() function.
						preparationSteps - List of preparation steps
			Returns : Nothing
		'''
		print "\n\n\n"
		link_inserted = False
		
		print "=> Entered into function insertPreparationTableEntry"
		prepStepList = list(preparationSteps)
		
		if len(preparationSteps) == 0:
			prepStepList.append('<a href="%s">Click here to view preparation method</a>' % (link))
			link_inserted = True
			
		modified_step = ''	
		for step in prepStepList:
			if not link_inserted:
				modified_step = mysql.escape_string(self.escape(step.strip().encode('UTF-8','ignore')))
			else:
				modified_step = mysql.escape_string(step.strip().encode('UTF-8','ignore'))
			
			self._cursor.execute("INSERT INTO recipe_preparation_method (prep_text, nid, prep_img) VALUES ('%s', '%s', 'None');" % (modified_step, nid))
			#self._connection.commit()
			
	def printData(self):
		print "Host : " + self.dbhost
		print "User : " + self.dbuser
		print "Password : " + self.dbpassword
		print "Database : " + self.db
		
	def recipeExists(self, recipe):
		'''This function checks for particular recipe in database.
			If it exists, it returns True otherwise False
		'''
	
	
		
		
# DataManager test
# d = DataManager('localhost','root','','thatsc5_newtcbdb',3306)

#vid = d.insertNodeRevisionTableEntry('Test Title') # Working
#nid = d.insertNodeTableEntry(vid, 'Test Title') # Working
#print d.insertTaxonomyTablesEntry('Dessert')
#print d.insertImageTableEntry('test1.jpg',r'www.test.com/test1.jpg', 1000, 'image/png')
#rnid = insertRecipe()
#d.insertPreparationTableEntry(rnid,['Take one tea spoon tea','Make a boiled water', 'Put a tea in boling water', 'Put a sugar in boiling water'])
#d.insertRecipeIngredientsTableEntry(rnid,['Sugar','Tea','Milk']) # Working
#print d.insertRecipeTableEntry(title="Test Title", source='Test Source', yields=10, description='Test Description', preptime='200', cooktime='300', calories='3000', fat='50%', saturates='60%', salt='80%', sugar='50%', recipe_image='5', categories = '6')

#d.insertRecipe(recipe.Recipe('www.recipe.com/test.html','Test Recipe', 'Test Recipe Description', 1000,10,20,30,['Sugar','Salt'],['Create boliled water','Add sugar'],10,20,30,40,50,60,'Test Tags','Test keywords','Test Tags'))

#print "Nid :" + str(nid)
#print d.getFilenameAndExtension("http://www.taste.com.au/recipes/28003/chicken+pasta+bakes")