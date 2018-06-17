import os


folderpath = "Downloaded index files"

names = os.listdir(folderpath)
actual_ordered_names = sorted(names)

for filename, name in zip(actual_ordered_names,sorted(names)[::-1] ):
	old_fullname = os.path.join(folderpath,filename)
	new_fullname = os.path.join(folderpath, name+"_")
	os.rename(old_fullname, new_fullname)

names = os.listdir(folderpath)
for filename in sorted(names):
	old_fullname = os.path.join(folderpath,filename)
	new_fullname = old_fullname.replace("_","")
	os.rename(old_fullname, new_fullname)

print(folderpath + ": order is fixed")


