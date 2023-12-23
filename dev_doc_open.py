import os
import webbrowser

docDir = os.path.join(os.getcwd(), "docs", "development", "build", "html", "index.html")
# open in browser, see https://stackoverflow.com/questions/40905703/how-to-open-an-html-file-in-the-browser-from-python
url = "file://" + docDir
webbrowser.open(url,new=2) # open in a new tab, if possible