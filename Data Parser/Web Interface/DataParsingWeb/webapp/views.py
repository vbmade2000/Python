# Create your views here.
from BaseHTTPServer import BaseHTTPRequestHandler
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from webapp.models import User, Settings
from django.template import RequestContext
import subprocess
import os
from crontab import CronTab


def index(request):
    vals = {}
    if isUserLoggedIn(request):
        print "User logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("webadmin")
    else:
        if request.GET.get("val", False):
            vals["error"] = "Invalid credentials"
            print "User not logged in : " + str(request.session.get("user_id", False))
        return  render_to_response("index.html", vals, context_instance=RequestContext(request) )

@csrf_exempt
def login(request):
    print "Login view started"
    print "User logged in : " + str(request.session.get("user_id", False))
    username = request.POST.get("username", None)
    password = request.POST.get("password", None)
    vals = {}
    if not username or not password:
        print "Please enter credentials"
        vals['error'] = "Invalid credentials"
        request.session["error"] = "Invalid credentials"
        return HttpResponseRedirect("/?val=1",)
    elif not isUserExists(username, password):
        print "Invalid credentials"
        vals['error'] = "Invalid credentials"
        return HttpResponseRedirect("/?val=1")
    else:
        setUserLoggedIn(request, username)



        print "&&&&&&&&&&&&&&&&& : " + request.session['user_id']
        print "Sessino value written"
        return HttpResponseRedirect("webadmin")

def webadmin(request):
    '''
        Controller to handle /webadmin url
    '''

    # Check if user is logged in. If not logged in then redirect  to index page
    if not isUserLoggedIn(request):
        print "User not logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("/")
    print "User logged in : " + str(request.session.get("user_id", False))
    values = {}
    # Retrieving value of sitemapurlfilepath key from database
    sitemapfilevalue_objlist = Settings.objects.filter(settingkey="sitemapurlfilepath")
    if len(sitemapfilevalue_objlist) > 0:
        sitemapfilevalue = sitemapfilevalue_objlist[0].settingvalue
        values["sitemapfilepath"] = sitemapfilevalue
        print "Value from Database : " + str(sitemapfilevalue)
        # Read sitemapurl file from disk if path exists in database
        if len(sitemapfilevalue.strip()) > 0:
            print "Site^^^^^^^^^^^^^^^^^^" + sitemapfilevalue
            sitemapurldata = readFile(sitemapfilevalue)
            values["sitemapurldata"] = sitemapurldata
        else:
            values["sitemapurldata"] = ""
    else:
        values["sitemapfilepath"] = ""
        values["sitemapurldata"] =  ""

    # Retrieving value of urlfilepath key from database
    urlfilepath_objlist = Settings.objects.filter(settingkey="urlfilepath")
    if len(urlfilepath_objlist) > 0:
        urlfilevalue = urlfilepath_objlist[0].settingvalue
        values["urlfilevalue"] = urlfilevalue
        print "Value from Database : " + str(urlfilevalue)
        # Read urlfile file from disk if path exists in database
        if len(urlfilevalue.strip())>0:
            urlfiledata = readFile(urlfilevalue)
            values["urlfiledata"] = urlfiledata
        else:
            values["urlfiledata"] = ""
    else:
        values["urlfilevalue"] = ""
        values["urlfiledata"] = ""

    return render_to_response("admin.html", values, context_instance=RequestContext(request))

def isUserExists(uname, pwd):
    '''
        Check if user exists in database or not
    '''
    users = User.objects.filter(username=uname, password=pwd)
    if len(users) >0:
        print "Access granted"
        return True
    else:
        print "Access denied"
        return False

@csrf_exempt
def settings(request):
    '''
        View for settings interface
    '''
    # Check if user is logged in. If not logged in then redirect  to index page
    if not isUserLoggedIn(request):
        print "User not logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("index")

    print "Settings view called"

    # Get username and password setting
    username = request.POST.get("username",False)
    password = request.POST.get("password",False)

    # Get sitemap file setting
    sitemapurlpath = request.POST.get("sitemapurlfilepath",False)

    # Get url file setting
    urlfilepath = request.POST.get("urlfilepath",False)

    # Save credentials
    user = User.objects.all()[0]
    user.username = username
    user.password = password
    user.save()

    # Save other settings ########################################################
    # Saving/Updating sitemapfile data
    obj_sitemapurlpath = Settings.objects.filter(settingkey="sitemapurlfilepath")
    if len(obj_sitemapurlpath) > 0:
        obj_sitemapurlpath = obj_sitemapurlpath[0]
        obj_sitemapurlpath.settingvalue = sitemapurlpath
        obj_sitemapurlpath.save()
    else: # If "sitemapurlfilepath" does not exists in database table
        sitemapfilesetting = Settings(settingkey="sitemapurlfilepath", settingvalue=sitemapurlpath)
        sitemapfilesetting.save()

    # Saving/Updating urlfile data
    obj_urlfilepath = Settings.objects.filter(settingkey="urlfilepath")
    if len(obj_urlfilepath) > 0:
        obj_urlfilepath = obj_urlfilepath[0]
        obj_urlfilepath.settingvalue = urlfilepath
        obj_urlfilepath.save()
    else: # If "urlfilepath" does not exists in database table
        urlfilesetting = Settings(settingkey="urlfilepath", settingvalue=urlfilepath)
        urlfilesetting.save()

    return HttpResponseRedirect("webadmin")

def readFile(filename):
    '''
    Read data from <filename>
    :param filename: name of file to be read
    :returns data if file exists, blank otherwise
    '''
    data = ""
    print "readFile() function started"
    print "filename : " + filename
    if os.path.isfile(filename):
        f = open(filename, "r")
        data = f.read()
        f.close()
    else:
        data = "File does not exist"
    print "readFile() function completed"
    return data


def writeFile(filename, data):
    '''
    Function to write data to file
    :param filename: name of file to write data
    :param data: data to be written in file
    '''
    print "writeFile is called"
    f = open(filename, "w")
    f.write(data)
    f.close()


@csrf_exempt
def saveurl(request):
    '''
    View to save url file data
    '''
    # Check if user is logged in. If not logged in then redirect  to index page
    if not isUserLoggedIn(request):
        print "User not logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("index")
    print "User logged in" + str(request.session.get("user_id", False))
    urlfiledata = request.POST.get("urlfiledata", False)
    if urlfiledata:
        urlfilepath = Settings.objects.filter(settingkey="urlfilepath")
        if len(urlfilepath)>0:
            urlfilepath = urlfilepath[0].settingvalue.strip()
            if len(urlfilepath) >0:
                writeFile(urlfilepath, urlfiledata.strip())

    return HttpResponseRedirect("webadmin")

@csrf_exempt
def sitemapurlview(request):
    '''
    View to save sitemap file data
    '''
    # Check if user is logged in. If not logged in then redirect  to index page
    if not isUserLoggedIn(request):
        print "User not logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("index")
    print "User logged in" + str(request.session.get("user_id", False))
    sitemapfiledata = request.POST.get("sitemapfiledata", False)
    if sitemapfiledata:
        sitemapfilepath = Settings.objects.filter(settingkey="sitemapurlfilepath")
        if len(sitemapfilepath)>0:
            sitemapfilepath = sitemapfilepath[0].settingvalue.strip()
            if len(sitemapfilepath) >0:
                writeFile(sitemapfilepath, sitemapfiledata.strip())

    return HttpResponseRedirect("webadmin")

def isUserLoggedIn(request):
    '''
    Function to check that user is logged in.
    It checks for particular username in session.
    If exists returns True, otherwise False.
    '''
    if request.session.get("user_id", False):
        print "User:::::::::: " + str(request.session.get("user_id", False))
        print "Used logged in"
        return True
    else:
        print "Used not logged in"
        print "User:::::::::: " + str(request.session.get("user_id", False))
        return False

def setUserLoggedIn(request, username):
    '''
    Function to set user_id value and make user logged in.
    '''
    request.session['user_id'] = username
    request.session.save()
    request.session.modified = True

@csrf_exempt
def logout(request):
    '''
    View to logout from site. Clears the session.
    '''
    try:
        del request.session['user_id']
    except KeyError:
        pass
    return HttpResponseRedirect("/")

@csrf_exempt
def executeScript(request):
    '''
    View to execute script from web interface
    '''
    print "Execute script view called"
    # Check if user is logged in. If not logged in then redirect  to index page
    if not isUserLoggedIn(request):
        print "User not logged in : " + str(request.session.get("user_id", False))
        return HttpResponseRedirect("index")

    iscronjob = request.POST.get("croncheck", False)
    if iscronjob == False:
        print "Direct execution selected"
        basepath =  os.path.dirname(os.path.abspath(__file__))
        filepath = basepath + os.path.sep + "script" + os.path.sep + "dataintegrator.py"
        argpath = basepath + os.path.sep + "script" + os.path.sep + "urls.txt"
        print "FilePath : " + filepath
        print "ArgPath : " + argpath

        test = subprocess.Popen(["python", filepath, argpath], shell=False)
        print "###########Result of execution is : " + str(test)

    else: # If cron job checkbox is checked, run script as a cron job
        print "Cron job option selected"
        tab  = CronTab()
        cron_job = tab.new("testcmd oauthstring")
        print "Type of cron job is $$$$$$$: " + str(cron_job )



    return HttpResponseRedirect("webadmin")



