import glob
import os.path
import os


# Fonction qui récupère la liste des fichier UI (Qt Designer)
def listuifiles(path):
	fichiers = []
	l = glob.glob(path+'\\*')
	for i in l:
		fichiers.append(i)
	return fichiers

	
# Fonction qui établi la liste des fichiers python correspondant aux dessins des fichiers UI
def listpyfiles(files):
	output = []
	for f in files:
		tmp_in = f.split("\\")
		tmp_out = ""
		for t in tmp_in:
			if(t == "ui_files"):
				t = "gen_files"
			if(".ui" in t):
				fichier_python = t.split(".")
				t = fichier_python[0] + ".py"
			if(t == "."):
				tmp_out = "."
			else:
				tmp_out = tmp_out + "\\" + t
		output.append(tmp_out)
	return output

	
# Fonction qui génère les fichiers python à partir des fichiers UI puis stockés dans le module gen_files
def generatePythonFiles(f_in, f_out):
	for i in range(len(f_in)):
		os.system("pyuic5 " + f_in[i] + " -o " + f_out[i])
	
files_in = listuifiles(".\\ui_files")
files_out = listpyfiles(files_in)
generatePythonFiles(files_in, files_out)