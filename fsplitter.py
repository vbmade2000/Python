# File Splitter
# Description  : Python script to split file into parts and join parts
# Developed by : Malhar Vora
# Email : vbmade2000@gmail.com
# Web   : http://malhar2010.blogspot.com
# Web   : http://byteofcloud.blogspot.com
################################################################3
import os
import sys

''' Function to split file in given size '''
def splitfile(filename, partsize):
    filelength = os.path.getsize(filename)
    sfile = open(filename,"rb")
    data = sfile.read()
    bytecounter = 0
    filecounter = 1
    ofile = open(filename + "." + str(filecounter),"wb")

    for byte in data:
        if (bytecounter % partsize ==0 ):
            ofile.close()
            ofile = open(filename + "." + str(filecounter),"wb")        
            filecounter += 1
        ofile.write(byte)    
        bytecounter += 1
    
    ofile.close()
    sfile.close()    

''' Function to join given parts into single file '''
def joinfiles(firstfilename):
    filenameparts = firstfilename.split(".")
    ofilename = filenameparts[0] + "." + filenameparts[1]
    ofile = open(ofilename,"wb")
    filecounter = 1
    filenameparts[2] = "1"
    infilename = ".".join(filenameparts)
    while(1):
        if (os.path.exists(infilename)):
            ifile = open(infilename, "rb")
            ofile.write(ifile.read())
            ifile.close()
        else:
            return
        filecounter += 1
        filenameparts[2] = str(filecounter)
        infilename = ".".join(filenameparts)


def printusage():
    print "FSplitter"
    print "Versino : 1.0"
    print "Developed by Malhar Vora"
    print "Usage : fsplitter.py option filename"
    print "Option"
    print "\t-s splitfile partsize unit(Ex. fsplitter.py -s setup.exe 1 mb)"
    print "\t\tUnits : kb,mb,gb"
    print "\t-j joinfile (Ex. fsplitter.py -j setup.exe.1)"
    

if len(sys.argv) <2:   
    print "Please enter correct parameters"
    printusage()
    sys.exit(2)

option = sys.argv[1]
if option=="-s":
    if len(sys.argv)== 2: # Filename missing
        print "Please enter filename"
        sys.exit(2)
    if len(sys.argv)== 3: # Partsize missing
        print "Please enter partsize"
        sys.exit(2)
    if len(sys.argv)== 4: # Unit missing
        print "Please enter unit"
        sys.exit(2)
        
    filename = sys.argv[2] # Filename
    partsize = long(sys.argv[3]) # Part size 
    unit =  sys.argv[4] # Unit of size

    # Check if file exists 
    if not os.path.exists(filename):
        print "File not found : " + filename
        sys.exit(2)

    # Check for data unit 
    if unit=="kb":
        byteval = (partsize*1024*100000)/100000
    elif unit=="mb":
        byteval = (partsize*1048576*100000)/100000
    elif unit=="gb":
        byteval = (partsize*1073741824*100000)/100000
    else:
        print "Wrong unit"
        sys.exit(2)

    print "Split operation started..."
    splitfile(filename, byteval)
    print "Operation completed"
    
elif option =="-j":
    
    filename = sys.argv[2] # Filename
    # Check if file exists 
    if not os.path.exists(filename):
        print "File not found : " + filename
        sys.exit(2)

    print "Join operation started..."
    joinfiles(filename)
    print "Operation completed"
else:
    print "Oops wrong option"
    
