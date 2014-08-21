from libs.datareader import parse_sitemap
from libs.datareader import getSiteMapUrl
from parsers.recipe import Recipe
from datalayer.datalayer import DataManager






#from lib import datareader.getSiteMapUrl


# Test the functions 	
# parse_sitemap(getSiteMapUrl("http://www.allrecipes.com"))
r = Recipe("http://thaifood.about.com/od/thaisnacks/r/greenmangosalad.htm","Green Mango Salad")
dm = DataManager('localhost', 'root', '', 'test')
dm.printData()





