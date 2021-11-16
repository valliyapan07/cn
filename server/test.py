from bs4 import BeautifulSoup
import os

def rename_file(old, new):
  try:
    if os.path.exists(old):
      os.rename(old, new)
      with open("index.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
      print("mm")
      div = soup.find("div", {"id": old})
      print(div['id'])
      div['id'] = new
      a = soup.find("a", {"href": "/server/" + old})
      print(a['href'])
      a['href'] = "/server/" + new
      a.string = new
      inp = soup.find("input", {"id": "/server/" + old})
      inp['id'] = "/server/" + new
      print("changed")
      cont = soup.prettify()
      with open("index.html", 'w') as f:
        f.write(cont)
      return True
    else:
      print("error..")
      return False
  except:
    return False

if rename_file("basics.txt","new.txt"):
    print("yes")
else:
    print("no")