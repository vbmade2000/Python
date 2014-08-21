# Import required functions and classes
from libs.datareader import parse_sitemap_recursively
from libs.datareader import getSiteMapUrl
from libs.datareader import readUrlsFromFile
from libs.datareader import getDataFromUrl
from parsers.recipe import Recipe
from datalayer.datalayer import DataManager

# Import parsers for various formats
from parsers.schemaparser import parseSchemaOrgData
from parsers.datavocabrecipeparser import parseDataVocabularyData
from parsers.hrecipeparser import parsehRecipeData
from parsers.rdfparser import parseRdfData

# Import other useful libraries
import hashlib
import sqlite3
import settings
import os
import urllib
import logging
import sys
import urlparse
import BeautifulSoup

logging.basicConfig(filename='ignoredurls.log',level=logging.INFO)


# Function to read mapping file from settings directory
def getMappingData(mappingfile):
	'''This function reads data from <mappingfile>, Store each mapping in dictionary 
		and returns that dictionary. 
		It uses <urlparse> library to get path from whole url.
		param : mappingfile - A file from which mapping data has to be read.
		returns : Dictionary containing { <domainname> : <uid> }
	'''
	mappingdict = {} # Dictionary to hold mapping data
	f = open(mappingfile)
	mappings = f.readlines()
	mappings = [mapping.strip() for mapping in mappings]  # Stripping \n in each line
	for mapping in mappings:
		entry = mapping.split(",")
		link = extractDomainWithExtension(entry[0])
		mappingdict[link] = entry[1]
	return mappingdict
		
	
def extractDomainWithExtension(url):
	'''This function extracts name of domain and extension.
	   i.e from www.food.com it extracts food.com
	   It uses urlparse module.
	   Returns domain.extension
	'''
	if not url.startswith("http://"):
		url = "http://" + url
	parts = urlparse.urlparse(url)
	return str(parts.netloc.lstrip("www."))		
	 

# Function to log message
def logData(message):
	'''This function simply logs the data to console.
	   It uses logging library.
	'''
	logging.info(message)
			
# Function to check that url is visited in past or not
def isUrlVisited(url, conn):
	'''This function checks whether given <url> exists in database table or not.
		If exists then returns True. False otherwise.
		It uses hashlib and sqlite3 libraries.
	'''
	# Calculate md5 hash of given <url> using hashlib library
	urlhash = hashlib.md5(url.encode("UTF-8")).hexdigest().strip()
	
	# Check if database table contains <urlhash>
	# cursor = conn.execute("SELECT count(*) FROM " + settings.VISITED_URL_TABLE + " WHERE urlhash='" + urlhash + "'")
	cursor = conn.execute("SELECT count(*) FROM tblVisitedUrls WHERE urlhash='" + urlhash + "'")
	
	count = cursor.fetchone()[0]
	
	if count>0: # It means the database table contains the <urlhash>
		return True
	else:
		return False
		
# Function to insert url into database table
def insertVisitedUrl(url, conn):
	'''This function simply inserts md5 of passed <url> in datavase table
	   It uses hashlib and sqlite3 libraries.	
	'''
	# Calculate md5 hash of given <url> using hashlib library
	urlhash = hashlib.md5(url.strip().encode("UTF-8")).hexdigest().strip()
	test = conn.execute("INSERT INTO " + settings.VISITED_URL_TABLE + "(urlhash) VALUES('" + urlhash + "')")
	conn.commit()

# Function to check that particular format keyword exists in data 
def checkForFormat(htmldataa, format_specifier):
	'''This function is used to check whether format specifier
	   for particular string exists in htmldata.
	   Return True if FOund, False otherwise
	'''
	ret = True
	b = BeautifulSoup.BeautifulSoup(htmldataa)
	data = b.find(itemtype=format_specifier)
	if data is None:
		ret = False
	return ret
	
# Function to grab data using various parsers
def grabData(url):
	'''This function downloads html data from given <url> and 
		passes it to various parsers, creates Recipe objects from parsed data
		and returns list of them
		It uses urllib library.
	'''
	recipelist = [] # List to hold recipe objects 
	itemsfound = 0
	print "URL being scanned: " + url  
	
	# Code refactored
	# ---- Old Code ----
	# htmldata = urllib.urlopen(str(url)).read() # Download html data from <url>
	# ---- New Refactored Code ----
	htmldata = getDataFromUrl(str(url)) # Download html data from <url>
	print "Length of htmldata : " + str(len(htmldata))
	# Check if data has itemtype="http://data-vocabulary.org/Recipe element.
	# If it is present then scan for related information
	datavocabpresent = htmldata.lower().find('itemtype="http://data-vocabulary.org/Recipe"'.strip().lower())
	print "datavocabpresent => " + str(datavocabpresent)
	 
	if datavocabpresent >-1:
		datavocabitems = parseDataVocabularyData(htmldata, url) # Grab data-vocabulary.org format data from url
		print "DataVocab Items : " + str(len(datavocabitems))
		itemsfound = itemsfound + len(datavocabitems)
		recipelist.extend(datavocabitems)
	
	# Check if data has itemtype="http://schema.org/Recipe" element.
	# If it is present then scan for related information
	schemaorgpresent = htmldata.lower().find('itemtype="http://schema.org/Recipe"'.strip().lower())
	print "schemaorgpresent => " + str(schemaorgpresent)
	if schemaorgpresent >-1:
		schemaitems = parseSchemaOrgData(htmldata, url) # Grab Schema.org/Recipe format data from url
		print "Schema.org Items : " + str(len(schemaitems))
		itemsfound = itemsfound + len(schemaitems)
		recipelist.extend(schemaitems)	
	
	# Check if data has xmlns:v="http://rdf.data-vocabulary.org/#" element. 
	# If it is present then scan for related information
	rdfpresent = htmldata.lower().find('xmlns:v="http://rdf.data-vocabulary.org/#"'.strip().lower())
	if rdfpresent >-1:
		rdfitems = parseRdfData(htmldata, url) # Grab RDFa format data from url
		print "RDFa Items : " + str(len(rdfitems))
		itemsfound = itemsfound + len(datavocabitems)
		recipelist.extend(rdfitems)
	
	# Check for hRecipe format
	hrecipeitems = parsehRecipeData(htmldata, url) # Grab hRecipe format data from url
	print "hRecipe Items : " + str(len(hrecipeitems))
	itemsfound = itemsfound + len(hrecipeitems)
	recipelist.extend(hrecipeitems)
	
	if itemsfound == 0:
		logData(url)
	
	return recipelist
	
# Function to extract data from a single url
def grabDataFromSingleUrl(url, mappingdict):
	'''This function extracts data of different format from a single url 
		most probably supplied from command line argument
	'''	
	print "Entered into grabDataFromSingleUrl() function"
	grabbedData = grabData(url)
	print "Length of grabbed data : " + str(len(grabbedData))
	if len(grabbedData)>0:	#Check if grabbedData list at least has some Recipes 
		datamanager = DataManager(settings.DATABASE_HOST, settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME, settings.DATABASE_PORT, mappingdict, settings.IMAGE_STORAGE_PATH, settings.RESIZED_IMAGE_STORAGE_PATH)
		for item in grabbedData:
			print "PrepTime : " + item.prepTime
			datamanager.insertRecipe(item)	
	print "Task completed"
	
# Main execution starts from here	
def main(mappingdict):
	# Check if input file exists 
	if(os.path.isfile(settings.SITEMAP_FILE)): 
		print "Reading file : " + settings.SITEMAP_FILE
		sitemaplist = readUrlsFromFile(settings.SITEMAP_FILE) # Read sitemap urls from input file

		conn = sqlite3.connect(settings.VISITED_URL_DATABASE)	
		
		#conn = sqlite3.connect("visitedurls.db")	
		for i in sitemaplist:
			datamanager = DataManager(settings.DATABASE_HOST, settings.DATABASE_USER, settings.DATABASE_PASSWORD, settings.DATABASE_NAME, settings.DATABASE_PORT, mappingdict, settings.IMAGE_STORAGE_PATH)

			urls = parse_sitemap_recursively(getSiteMapUrl(i)) # Fetch all urls from sitemap
			
			for url in urls:
				if not isUrlVisited(url, conn):				
					
					grabbedData = grabData(url)
					if len(grabbedData)>0:	#Check if grabbedData list at least has some Recipes 
						for item in grabbedData:
						
							datamanager.insertRecipe(item)				
					insertVisitedUrl(url, conn)
	else:
		print "File does not exists"
			
if __name__ == "__main__":
	print "Script execution started..."
	
	# Read mapping file
	print "Started reading mapping file " + settings.MAPPING_FILE
	mappingdict = getMappingData(settings.MAPPING_FILE)
	print "Reading mapping file completed"

	# Check if command-line input is given 
	# If input is given then extract information from urls given supplied file
	if len(sys.argv)>1: 
		print "Command line input found"
		print "Reading file " + sys.argv[1]
		individual_url_filename  = sys.argv[1]
		f = open(sys.argv[1])
		urls = f.readlines()
		f.close()
		print "Urls : " + str(urls)
		if len(urls)>0:
			for url in urls:
				grabDataFromSingleUrl(url.strip("\n"), mappingdict) # .strip("\n")
		else:
			print "The file supplied does not contain any url"
			
	else: # Go for scanning sitemapurls.txt if exists in current directory
		print "Command line input is not found"
		main(mappingdict)
	
	



	
 
