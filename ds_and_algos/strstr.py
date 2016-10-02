# This program implements strstr() function of C aka finding substring in a string
main_str = "Hello World"
substr = " World"

# Using built in function
len_substr = len(substr)
position = -1
try:
    for i in range(len(main_str)):
        if main_str[i:len_substr+i] == substr:
            position = i
            break
except:
    print "Exception"

print "Position :" + str(position)

# Without using built in functions
position = -1

for i in range(len(main_str)):
    c = 0
    found = False
    for j in range(i, len_substr+i):
        if main_str[j] == substr[c]:
            found = True
        else:
            found = False
            break
        c+=1
    if found:
        position = i
        break
print "Position = " + str(position)
