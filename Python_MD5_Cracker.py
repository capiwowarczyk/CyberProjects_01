#This is my Python MD5 hash cracker!!

import hashlib, time

hash = str(input("Enter your hash here: ")) #getting user input
print("Attempting to find the password...")

start = time.time() #starting a timer

for i in range(1, 99999999999):  #attempting to crack the given hash
    guess = hashlib.md5(repr(i).encode('utf-8')).hexdigest
    if guess == hash:
        print("Password Found: ", i) #prints the found hash
        break

end = time.time()
print("Found in: ",end-start,"seconds") #prints the found hash and how long it took to find the hash