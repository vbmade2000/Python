class Recipe:
    '''This class represents a single Recipe'''
        
    def __init__(self, rlink, rname, rdescription='', rimage='', rpreptime='', rcooktime='', rservings='',
                 ringredients=[], rpreparation=[], rcalories='', rfat='', rsaturatedfat='', rsalt='',
                 rsugar='', rratings='', rtags='', rkeywords='', rcategories=''):
    
        self.link = rlink # Link to recipe with website
        self.name = rname.encode('UTF-8','ignore') # Name of the recipe
        self.description = rdescription.encode('UTF-8','ignore') # Description of recipe
        self.image = rimage # Image url of recipe
        self.prepTime = rpreptime.encode('UTF-8','ignore') # Preparation time for recipe
        self.cookTime = rcooktime.encode('UTF-8','ignore') # Cooking time for recipe
        self.servings = rservings.encode('UTF-8','ignore') # No of servings/yield of recipe
        self.ingredients = ringredients # Ingredients used in recipe (Can be more than one)
        self.preparation = rpreparation # Preparation instructions for recipe (Can inclue multiple steps)
        self.calories = rcalories.encode('UTF-8','ignore') # Calories of recipe
        self.fat = rfat.encode('UTF-8','ignore') # Fat content in recipe
        self.saturatedFat = rsaturatedfat.encode('UTF-8','ignore') # Saturated fat content in recipe
        self.salt = rsalt.encode('UTF-8','ignore') # Salt in recipe
        self.sugar = rsugar.encode('UTF-8','ignore') # Sugar used in recipe
        self.ratings = rratings.encode('UTF-8','ignore') # Ratings given to recipe by users
        self.tags = rtags.encode('UTF-8','ignore') # Tags assigned to recipe
        self.keywords = rkeywords.encode('UTF-8','ignore') # Keywords assigned to recipe
        self.categories = rcategories.encode('UTF-8','ignore') # Categories assigned to recipe (e.g SeaFood, Desert etc. Can be multiple)
