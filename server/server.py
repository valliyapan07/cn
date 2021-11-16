import socket
import os
from bs4 import BeautifulSoup
from _thread import *
from datetime import datetime

def modification_date(filename):
  t = os.path.getmtime(filename)
  return datetime.fromtimestamp(t).strftime("%a, %d %b %Y %X" + " GMT")

def get_request(c, request):
  data = request
  ind1 = data.index('/') + 1
  ind2 = data.index(' ', ind1)
  name = data[ind1:ind2]
  resp_str = "HTTP/1.1 200 OK"
  if name != "favicon.ico" and len(name) > 1 and not name.endswith(".jpg"):
    if name.__contains__("?"):
      i = name.index("oldname") + 8
      j = name.index("&")
      old = name[i:j]
      new = name[j + 9:]
      print("old = ", old)
      print("new = ", new)
      if len(new.encode('utf-8')) > 150:
        resp_str = "HTTP/1.1 501 Not Implemented\n\n" + "<h2>File length too large.</h2>"
      else:
        if rename_file(old, new):
          resp_str = resp_str + "\n\n" + "<h2>" + old + \
             " is changed to " + new + ".</h2>"
        else:
          resp_str = "HTTP/1.1 404 Not Found\n\n" + \
              "<h2>" + "404 " + old + " not found.</h2>"  
    else:
      try:
        if name == "server" or name.startswith("server") or name == "index.css":
          if name == "server":
            name = "index.html"
          elif name.startswith("server"):
            i = name.find('/')
            name = name[i+1:]
          with open(name) as f:
            print(name)
            cont = f.read()
            leng = len(cont)
            mod_time = modification_date(name)
            time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
            resp_str = resp_str + "\r\n" + time + "Server: Valliyapan SM\r\n" + \
              "Connection: close\r\n" + \
              "Content-Length: " + \
              str(leng) + "\r\n" + \
              "Last-Modified: " + mod_time + "\r\n"
            if name.endswith(".html"):
              resp_str = resp_str + "Content-Type: text/html\n\n"
            elif name.endswith(".css"):
              resp_str = resp_str + "Content-Type: text/css\n\n"
            else:
              resp_str = resp_str + "Content-Type: text/plain\n\n"
            resp_str = resp_str + cont
        else:
          raise Exception("Not Found")
      except Exception as e:
        print(e)
        resp_str = "HTTP/1.1 404 Not Found\n\n" + \
            "<h2>" + "404 " + name + " not found.</h2>"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)
  elif name == "favicon.ico" or name.endswith(".jpg"):
    try:
      if name.startswith("server"):
        i = name.find('/')
        name = name[i+1:]
      with open(name, "rb") as f:
        cont = f.read()
        leng = str(len(cont))
      if name.endswith(".jpg"):
        f_type = "Content-Type: image/jpeg"
        time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
        resp_str = resp_str + "\r\n" + time + "Server: Valliyapan SM\r\n" + \
            "Connection: close\r\n" + "Content-Length: " + leng + "\r\n" + f_type
        resp_str = resp_str + "\n\n"
    except:
      resp_str = "HTTP/1.1 404 Not Found\n\n" + \
          "<h2>" + "404 " + name + " not found.</h2>"
      resp_str = resp_str.encode('utf-8')
    if isinstance(resp_str, str):
      resp_str = resp_str.encode('utf-8') + cont
      c.sendall(resp_str)
      c.close()
      print("*" * 70)
      print("Response:")
      print(len(resp_str))
  else:
    time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
    resp_str = resp_str + "\r\n" + time + \
        "Server: Valliyapan SM\r\n" + "Connection: close\r\n"
    resp_str = resp_str + "Content-Type: text/html\n\n"
    resp_str = resp_str + "<h2>Thank you for connecting</h2>"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)


def post_request(c, request, img):
  data = request
  if data.__contains__("application/x-www-form-urlencoded"):
    data = data.split("\r\n")[-1]
    i = data.index("oldname") + 8
    j = data.index("&")
    old = data[i:j]
    new = data[j + 9:]
    print("old = ", old)
    print("new = ", new)
    if len(new.encode('utf-8')) > 150:
      resp_str = "HTTP/1.1 501 Not Implemented\n\n" + "<h2>File length too large.</h2>"
    else:
      if rename_file(old, new):
        resp_str = "HTTP/1.1 200 OK"
        resp_str = resp_str + "\n\n" + "<h2>" + old + \
            " is changed to " + new + ".</h2>"
      else:
        resp_str = "HTTP/1.1 404 Not Found\n\n" + \
            "<h2>" + "404 " + old + " not found.</h2>"
    c.send(resp_str.encode('utf-8'))
  elif data.__contains__("multipart/form-data"):
    fname = data.index("filename") + 10
    end1 = data.index('"', fname)
    name = data[fname:end1]
    print("name = " + name)
    data = data[fname:].split("\r\n")
    lis = os.listdir()
    if name in lis:
      count = lis.count(name)
      name = "(" + str(count) + ")" + name
    if name.endswith(".txt") or name.find(".") == -1 or name.endswith(".csv"):
      with open(name, 'w') as f:
        f.write(data[3])
        typ = "text/plain"
    elif name.endswith(".jpg"):
      with open(name, 'wb') as f:
        f.write(img)
      with open(name, 'rb') as f:
        last = f.readlines()[-1]
        img = img.split(last)[0]
      with open(name, 'wb') as f:
        f.write(img)
  else:
    resp_str = "HTTP/1.1 501 Not Implemented\n\n" + "<h2>501 Not Implemented.</h2>"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)
    return
  loc = "http://" + host + ":" + str(port) + "/server/" + name + "\r\n"
  disp = "<h2>" + name + " is uploaded to server.<h2>"
  resp_str = "HTTP/1.1 201 Created\r\n"
  time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
  resp_str = resp_str + time + \
      "Server: Valliyapan SM\r\n" + "Content-Location: " + loc + "Connection: close\r\n" + "Content-Type: text/html" + \
      "\r\nContent-Length: " + str(len(disp)) + "\n\n"
  resp_str = resp_str + disp
  c.send(resp_str.encode('utf-8'))
  add_list(name)
  c.close()
  print("*" * 70)
  print("Response:")
  print(resp_str)


def put_request(c, request, img):
 data = request
 fname = data.index("filename") + 10
 end1 = data.index('"', fname)
 name = data[fname:end1]
 lis = os.listdir()
 data = data[fname:].split("\r\n")
 if name.endswith(".txt") or name.find(".") == -1 or name.endswith(".csv"):
    with open(name, 'w') as f:
      f.write(data[3])
 elif name.endswith(".jpg"):
    with open(name, 'wb') as f:
      f.write(img)
    with open(name, 'rb') as f:
      last = f.readlines()[-1]
    img = img.split(last)[0]
    with open(name, 'wb') as f:
      f.write(img)
 else:
    resp_str = "HTTP/1.1 501 Not Implemented\n\n" + "<h2>501 Not Implemented.</h2>"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)
    return
 if name in lis:
    resp_str = "HTTP/1.1 204 No Content\r\n"
 else:
    add_list(name)
    resp_str = "HTTP/1.1 201 Created\r\n"
 loc = "http://" + host + ":" + str(port) + "/server/" + name + "\r\n"
 time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
 resp_str = resp_str + time + \
    "Server: Valliyapan SM\r\n" + "Content-Location: " + \
    loc + "Connection: close\r\n" + "\n\n"
 c.send(resp_str.encode('utf-8'))
 c.close()
 print("*" * 70)
 print("Response:")
 print(resp_str)


def head_request(c, request):
  data = request
  ind1 = data.index('/') + 1
  ind2 = data.index(' ', ind1)
  name = data[ind1:ind2]
  resp_str = "HTTP/1.1 200 OK\r\n"
  try:
    i = name.index('/')
    name = name[i+1:]
    if name.endswith(".jpg"):
      with open(name, "rb") as f:
        cont = f.read()
        leng = str(len(cont)) + "\r\n"
        f_type = "Content-Type: image/jpeg\r\n"
    else:
      with open(name, 'r') as f:
        cont = f.read()
        leng = str(len(cont)) + "\r\n"
        f_type = "Content-Type: text/html\r\n"
    mod_time = modification_date(name)
    time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
    resp_str = resp_str + "Content-Length: " + \
        leng + "Connection: close\r\n" + time + "Server: Valliyapan SM\r\n" + \
        f_type + "Last-Modified: " + mod_time + "\n\n"
  except Exception as e:
    resp_str = "HTTP/1.1 404 Not Found\n\n"
  c.send(resp_str.encode('utf-8'))
  c.close()
  print("*" * 70)
  print("Response:")
  print(resp_str)


def delete_request(c, request):
 data = request
 ind1 = data.index('/') + 1
 ind2 = data.index(' ', ind1)
 name = data[ind1:ind2]
 try:
    i = name.index('/')
    name = name[i+1:]
    os.remove(name)
    with open("index.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    div = soup.find("div")
    div.find("div", {"id": name}).decompose()
    cont = soup.prettify()
    with open("index.html", 'w') as f:
        f.write(cont)
        resp_str = "HTTP/1.1 204 No Content\r\n"
        time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
        resp_str = resp_str + time + "Connection: close\r\n" + \
          "Server: Valliyapan SM\n\n"
        c.send(resp_str.encode('utf-8'))
        c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)
 except Exception as e:
   print(e)
   resp_str = "HTTP/1.1 404 Not Found\n\n"
   c.send(resp_str.encode('utf-8'))
   c.close()


def rename_file(old, new):
  try:
    if os.path.exists(old):
      os.rename(old, new)
      with open("index.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
      div = soup.find("div", {"id": old})
      div['id'] = new
      a = soup.find("a", {"href": "/server/" + old})
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


def add_list(name):
  with open("index.html") as fp:
    soup = BeautifulSoup(fp, 'html.parser')
  div = soup.find("div", {"class": "files"})
  innerdiv = soup.new_tag('div')
  innerdiv.attrs['class'] = "file-box"
  innerdiv.attrs['id'] = name
  anch = soup.new_tag('a')
  anch.attrs['href'] = "/server/" + name
  anch.append(name)
  button = soup.new_tag('input')
  button.attrs['id'] = "/server/" + name
  button.attrs['class'] = "button"
  button.attrs['onclick'] = "del(this.id)"
  button.attrs['type'] = "button"
  button.attrs['value'] = "Delete"
  innerdiv.append(anch)
  innerdiv.append(button)
  div.append(innerdiv)
  cont = soup.prettify()
  with open("index.html", 'w') as f:
    f.write(cont)


def new_client(c, addr):
  request = ""
  img = b''
  flag = False
  while 1:
    req = c.recv(2048)
    data = req.split(b'\r\n\r\n')
    try:
      if not flag:
        request = request + req.decode().strip()
      else:
        raise Exception("hello")
    except Exception as e:
      flag = True
      j = 0
      l = len(data)
      for i in data:
        if j != l - 1:
          request = request + i.decode().strip() + "\r\n\r\n"
        else:
          img = img + i
          request = request + str(i)
        j = j + 1
    if len(req) < 2048:
      break
    elif len(req) == 2048:
      if request.endswith("\r\n\r\n"):
        break
      else:
        print("end characters:", request[-1])
        print("over..")
  if request.__contains__(' '):
    ind1 = request.index(' ')
    method = request[:ind1].lower()
  else:
    method = "close"
  if not len(img) > 1:
    print("*" * 70)
    print("Request:\n\n")
    print(request)
  else:
    print("*" * 70)
    print(f'Request:\n\n {method} request with an image in binary format')
    print("length of img = ", len(img))
  if method:
    if method == "get":
      if len(request) > 3072:
        resp_str = "HTTP/1.1 414 Request-URI Too Long\n\n" + \
            "<h2> 414 Request-URI Too Long</h2>"
        c.send(resp_str.encode('utf-8'))
        c.close()
      else:
        get_request(c, request)
    elif method == "head":
      head_request(c, request)
    elif method == "post":
      post_request(c, request, img)
    elif method == "put":
      put_request(c, request, img)
    elif method == "delete":
      delete_request(c, request)
    elif method == "close":
      c.close()
      print("breaking connection..")


def main():
  s = socket.socket()
  s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
  global host, port
  host = "localhost"
  port = 2002
  s.bind((host, port))
  s.listen(5)
  while True:
    print(f"server running on {host} in port number {port}..")
    c, addr = s.accept()
    print('Got connection from', addr)
    start_new_thread(new_client, (c, addr))
  s.close()
if __name__ == "__main__":
 main()