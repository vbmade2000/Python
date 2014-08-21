import os
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
import urlparse
import sys


# Globals
aurllist = []

# Function to get html data from given url 
def getDataFromUrl(url):
	'''This function downloads data from a given <url>
	   It uses urllib library.
	   #Return : htmldata if successfully downloaded. 
	'''
	print "Entered into getDataFromUrl() function"
	htmldata = ''
	
	try:
		urlobj = urllib.urlopen(url)
		print "Response Code : " + str(urlobj.code)
		if urlobj.code == 200:
			htmldata = urlobj.read()
			print "Length of html Data : " + str(len(htmldata))
	except IOError, ioerror:
		print "Failed to open url :" + str(url)
	return htmldata
		
	
	

# Function to retrieve extension of given url
def getUrlExtension(url):
    '''Returns extension (e.g html,xml,php etc) of given url
	   It uses urlparse library
	'''        
    path = urlparse.urlparse(url).path
    extension = os.path.splitext(path)[1] 
	
    return extension.strip()

# Function to read urls from text file
def readUrlsFromFile(file_location):
	'''Read data from a file located at <file_location> location
		Returns list of urls grabbed from file
		It uses os library
	'''
	print "\n"
	print "Entered into readUrlsFromFile() function"
	print "Reading from input file"
	urllist = []  #List to hold urls
	if(os.path.isfile(file_location)): 
		datafile = open(file_location,'r')
		lines = datafile.readlines()
		lines = [line.strip() for line in lines]  # Stripping \n in each line
		append = urllist.append
		for line in lines:
			append(line)
		datafile.close()
		print "readUrlsFromFile() completed"
		print "\n"
		return urllist
	else:
		return None
				
# Function to get sitemap path 		
def getSiteMapUrl(siteurl):
	'''Checks siteurl/robobt.txt for Sitempa url otherwise return siteurl/sitemap.xml'''
	
	print "Entered into getSiteMapUrl() function"
	print "Fetching sitemap url from given url"
	siteurl = siteurl.rstrip("/")
	print "$$$$$$$$$$:" + siteurl

	roboturl = siteurl + r'/robots.txt'
	print "###########-->" + roboturl
	
	# Code refactored
	# ---- Old Code ----
	# robotdata = urllib.urlopen(roboturl).read() # Reading robots.txt of given url
	# New refactored code
	robotdata = getDataFromUrl(roboturl) # Reading robots.txt of given url
	
	lines = robotdata.split("\n")
	sitemapurl = "" # Variable to hold sitemap url
	
	# Iterate through each line and check if it contains sitemap url
	for line in lines:
		if line.lower().find('sitemap:') > -1:
			print "Found"
			sitemapurl = line.strip()
	
	
	#If Robots.txt does not contain sitemap url then take direct url		
	
	if(len(sitemapurl) <= 0):
		print "Entered into if"
		sitemapurl = siteurl + "/sitemap.xml" 
	print "%%%%%%%%%%%%" + sitemapurl
	return sitemapurl[sitemapurl.find('http'):].strip()

# Function to get all urls from sitemap	
def parse_sitemap(url):
	'''Download xml data from given sitemap using urllib and parse it through 
	   BeautifulSoup library. Read urls tagged with <loc>, append to list 
	   and return that list
	'''	
	print "Entered into parse_sitemap function"
	print 'Started Parsing : ' + url
	# Code refactored
	# ---- Old Code ----
	# sitemapdata = urllib.urlopen(url).read()
	# New refactored code
	sitemapdata = getDataFromUrl(url)
	urllist = [] # List to hold fetched urls
	appendToUrlList = urllist.append
	soup = BeautifulSoup(sitemapdata)
	print 'Starting finding locs'
	locs = soup.findAll('loc')
	for loc in locs:
		appendToUrlList(loc.string)
	
	return urllist
	
# Function currently in testing and not finalized
# Function to parse sitemap recursively
def parse_sitemap_recursively(url):
	'''Recursively parse sitemap for urls and returns a list containing these urls.
	   Returns list of grabbed urls.
	'''
	print "Entered into parse_sitemap_recursively function"
	basesitemap = url
	print "Scanning through : " + url
	subdomainsitemaplist = [] # List to hold xml urls
	#aurllist = [] # List to hold nonxml urls
	global aurllist # List to hold nonxml urls
	
	appendToSubDomainSiteMapList = subdomainsitemaplist.append
	appendToUrlList = aurllist.append
	for urlitem in parse_sitemap(url):
		if getUrlExtension(urlitem) != '.xml':
			appendToUrlList(urlitem)		
		else:
			print "Found xml : " + urlitem
			appendToSubDomainSiteMapList(urlitem)
	print "#######################"
	print str(aurllist)
	# Get urls from each item from appendToSubDomainSiteMapList
	for subdomainsitemap in subdomainsitemaplist:
		parse_sitemap_recursively(subdomainsitemap)

	return aurllist
							


# Test for above function. Get sitemap url from given site and fetch all the urls from that sitemap.
#for i in parse_sitemap(getSiteMapUrl("http://allrecipes.com/recipehubs.xml")):
	# print i
#	print i
#for i in parse_sitemap("http://allrecipes.com/recipehubs.xml"):
#sitemapurl = getSiteMapUrl("http://www.astrowow.com/")

#l = parse_sitemap_recursively(sitemapurl)


		
