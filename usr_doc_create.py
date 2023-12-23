import os
import webbrowser

# install:
# pip install sphinx sphinx-autodocgen sphinx-rtd-theme sphinx-autodoc-typehints m2r2

thisDir = os.getcwd()
os.chdir("./docs/user")
docDir = os.path.join(os.getcwd(), "build", "html", "index.html")
print("Cleaning the directories...")
os.system("make clean html")
os.system("rm -r ./source/_autosummary")
os.system("rm -r ./source/autodocgen-output")
os.system("rm -r ./build/*")
print("Cleaning done. Start to create docs.")
os.system("make html")
print("Cleaning the directories...")
os.system("rm -r ./source/_autosummary")
os.system("rm -r ./source/autodocgen-output")
os.system("rm -r ./build/doctrees")
os.system("rm -r ./build/_sources")
print("Cleaning done.")
os.chdir(thisDir)
print("\nDocumentation created: ./docs/user/_build/html/index.html")
print("---------------------------------------------------------")



def main():
    # open in browser, see https://stackoverflow.com/questions/40905703/how-to-open-an-html-file-in-the-browser-from-python
    url = "file://" + docDir
    webbrowser.open(url,new=2) # open in a new tab, if possible

if __name__ == '__main__':
    main()