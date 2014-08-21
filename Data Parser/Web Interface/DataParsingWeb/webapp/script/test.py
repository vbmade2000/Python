import sys

print "test script execution started"

f = open(sys.argv[1])
print f.read()
f.close()
print "Execution completed"
