import re
import pandas as pd
import numpy as np
import os



def parse_folders(datafolder = 'Downloaded data files'):
	return [dirpath for (dirpath, dirnames, filenames) in os.walk(datafolder) if "download.log" in os.listdir(dirpath)  ]

def get_submission_text(folder):
	files = os.listdir(folder)
	sizes = [ os.path.getsize(folder+"/"+file) for file in files]	
	folder = os.path.abspath(folder)
	return   os.path.join ( folder , files[sizes.index(max(sizes))])

# by submission text 
def get_10k_htm(folder):

	submission_txt = get_submission_text(folder)
	htm = -1 # temporary index storer
	fp = open(submission_txt)
	for i, line in enumerate(fp):
		if "<TYPE>10-K" in line:
			htm = i+2
		if i == htm:
			htm = line.strip()[10:]
			break
	fp.close()
	return os.path.join(folder,htm)














