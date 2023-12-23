import os

thisDir = os.getcwd()
print("Cleaning the distibution directory...")
os.system("rm -r ./dist/*")
print("Done. Start making the distribution files.")
os.system("python3 -m pip install --upgrade build")
os.system("python3 -m build")
print("=============================================================================================")
print("To save distribution on Git: Remove 'dist'-directory from .gitignore or save it with Git-LFS.")
print("=============================================================================================\n")