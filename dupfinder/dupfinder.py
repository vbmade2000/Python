#This file is part of dupfinder.

#dupfinder is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.

#dupfinder is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with dupfinder.  If not, see <http://www.gnu.org/licenses/>.


import hashlib
import os
import sys

def get_file_checksum(filename):
    return hashlib.md5(open(filename).read()).hexdigest()

# Dictionary to hold files and list of their duplicates 
abs_file_path = ""
file_name = ""
file_list = None

def find_duplicates(dir_path):
    '''
        Traverses a directory tree, calculate MD5 hash of file content
		and put it in <files> dictionary. If hash is already present in
		<files> then it puts a tuple containing hash and absolute file 
		path (file_hash, abs_file_path) otherwise appends same tuple to
		list contained as value in <files> for that particular entry.
		Return a dictionary 
	'''
    # Traverse directory and fill files directory
    files = {}
    for dirName, subodirList, fileList in os.walk(dir_path):
        print "Scanning " + dirName
        for fname in fileList:
			abs_file_path = os.path.join(dirName, fname)
			file_hash = get_file_checksum(abs_file_path)
			if file_hash not in files:
				files.update({file_hash: [(file_hash, abs_file_path)]})
			else:
				temp_list = files[file_hash]
				temp_list.append((file_hash, abs_file_path))
				files[file_hash] = temp_list
    return files
    #print "Following is a list of file groups with same content"
    #print "====================================================\n"
    #for item in files.items():
    #    print "No of files : " + str(len(item[1]))
    #    file_list = item[1]
    #   for file in file_list:
    #        print file[1]
    #    print "----------------------------------"

		

def print_duplicates(files_dict):
    '''
	    Prints dictionary returned by find_duplicates() in a formatted way
	'''
    file_count = 0
    print "\nFollowing is a list of file groups with same content"
    print "===================================================="
    for item in files_dict.items():
        file_count = len(item[1])
        
        file_list = item[1]
        if file_count > 1:
            print "No of files : " + str(file_count)
            for file in file_list:
                print file[1]
            print "----------------------------------"

def print_usage():
    '''
	    Prints usage of utility
	'''
    print "Duplicate file finder"
    print "======================="
    print "Developed by : Malhar Vora"
    print "Email : mlvora.2010@gmail.com"
    print "Blog : http://malhar2010.blogspot.com"
    print "Usage: dupfinder <dir to scan>"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        dir_to_scan = sys.argv[1]
        print "dir_to_scan :" + str(dir_to_scan)
        print_duplicates(find_duplicates(dir_to_scan))
    else:
        print_usage()
