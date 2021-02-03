import socket
import sys
import os
from bs4 import BeautifulSoup
from _thread import *
from datetime import datetime


def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.fromtimestamp(t).strftime("%a, %d %b %Y %X" + " GMT")


def get_request(c, request):
    #print("inside get request..")
    data = request
    ind1 = data.index('/') + 1
    ind2 = data.index(' ', ind1)
    name = data[ind1:ind2]
    resp_str = "HTTP/1.1 200 OK"
    if name != "favicon.ico" and len(name) > 1:
        #print("name = " + name)
        with open(name) as f:
            cont = f.read()
            time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
            resp_str = resp_str + "\r\n" + time + "Server: Valliyapan SM\r\n" + \
                "Connection: Keep-Alive\r\n"
            if name.endswith(".html"):
                resp_str = resp_str + "Content-Type: text/html\n\n"
            elif name.endswith(".css"):
                resp_str = resp_str + "Content-Type: text/css\n\n"
            else:
                resp_str = resp_str + "Content-Type: text/plain\n\n"
            resp_str = resp_str + cont
        c.send(resp_str.encode('utf-8'))
        c.close()
        print("*" * 70)
        print("Response:")
        print(resp_str)
    elif name == "favicon.ico":
        with open(name, "rb") as f:
            cont = f.read()
        resp_str = resp_str + "\n\n"
        resp_str = resp_str.encode('utf-8') + cont
        c.sendall(resp_str)
        c.close()
        print("*" * 70)
        print("Response:")
        print(len(resp_str))
    else:
        time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
        resp_str = resp_str + "\r\n" + time + \
            "Server: Valliyapan SM\r\n" + "Connection: Keep-Alive\r\n"
        resp_str = resp_str + "Content-Type: text/html\n\n"
        resp_str = resp_str + "<h2>Thank you for connecting</h2>"
        c.send(resp_str.encode('utf-8'))
        c.close()
        print("*" * 70)
        print("Response:")
        print(resp_str)


def post_request(c, request):
    #print("inside post request..")
    data = request
    fname = data.index("filename") + 10
    end1 = data.index('"', fname)
    name = data[fname:end1]
    #print("name = " + name)
    data = data[fname:].split("\r\n")
    # print(data[3])
    with open(name, 'w') as f:
        f.write(data[3])
    resp_str = "HTTP/1.1 201 Created\r\n"
    time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
    resp_str = resp_str + time + \
        "Server: Valliyapan SM\n\n"
    resp_str = resp_str + "<h2>" + name + " is uploaded to server.<h2>"
    c.send(resp_str.encode('utf-8'))
    add_list(name)
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)


def put_request(c, request):
    #print("inside put request..")
    data = request
    fname = data.index("filename") + 10
    end1 = data.index('"', fname)
    name = data[fname:end1]
    #print("name = " + name)
    lis = os.listdir()
    data = data[fname:].split("\r\n")
    # print(data[3])
    with open(name, 'w') as f:
        f.write(data[3])
    if name in lis:
        resp_str = "HTTP/1.1 204 No Content\r\n"
    else:
        add_list(name)
        resp_str = "HTTP/1.1 201 Created\r\n"
    time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
    resp_str = resp_str + time + \
        "Server: Valliyapan SM\n\n"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)


def head_request(c, request):
    #print("inside head request..")
    data = request
    ind1 = data.index('/') + 1
    ind2 = data.index(' ', ind1)
    name = data[ind1:ind2]
    #print("name = " + name)
    resp_str = "HTTP/1.1 200 OK\r\n"
    with open(name, 'r') as f:
        cont = f.read()
    mod_time = modification_date(name)
    leng = str(len(cont))
    resp_str = resp_str + "Content-Length: " + \
        leng + "\r\nContent-Type: text/html\r\nLast-Modified: " + mod_time + "\n\n"
    c.send(resp_str.encode('utf-8'))
    c.close()
    print("*" * 70)
    print("Response:")
    print(resp_str)


def delete_request(c, request):
    #print("inside delete request..")
    data = request
    ind1 = data.index('/') + 1
    ind2 = data.index(' ', ind1)
    name = data[ind1:ind2]
    #print("name = " + name)
    try:
        os.remove(name)
        with open("index.html") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
        div = soup.find("div")
        div.find("div", {"id": name}).decompose()
        cont = soup.prettify()
        with open("index.html", 'w') as f:
            f.write(cont)
            resp_str = "HTTP/1.1 200 OK\r\n"
            time = "Date: " + datetime.now().strftime("%a, %d %b %Y %X" + " GMT") + "\r\n"
            resp_str = resp_str + time + \
                "Server: Valliyapan SM\n\n"
            c.send(resp_str.encode('utf-8'))
            c.close()
        print("*" * 70)
        print("Response:")
        print(resp_str)
    except Exception as e:
        print(e)


def add_list(name):
    with open("index.html") as fp:
        soup = BeautifulSoup(fp, 'html.parser')
    div = soup.find("div", {"class": "files"})
    innerdiv = soup.new_tag('div')
    innerdiv.attrs['class'] = "file-box"
    innerdiv.attrs['id'] = name
    anch = soup.new_tag('a')
    anch.attrs['href'] = name
    anch.append(name)
    button = soup.new_tag('input')
    button.attrs['id'] = name
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
    request = c.recv(4096).decode()
    print("*" * 70)
    print("Request:\n\n")
    print(request)
    if request.__contains__(' '):
        ind1 = request.index(' ')
        method = request[:ind1].lower()
    else:
        method = "close"
    if method:
        #print("method = ", method, "\n\n")
        if method == "get":
            get_request(c, request)
        elif method == "head":
            head_request(c, request)
        elif method == "post":
            post_request(c, request)
            #get_request(c, "GET /index.html HTTP/1.1")
        elif method == "put":
            put_request(c, request)
            #get_request(c, "GET /index.html HTTP/1.1")
        elif method == "delete":
            delete_request(c, request)
            #get_request(c, "GET /index.html HTTP/1.1")
        elif method == "close":
            c.close()
            print("breaking connection..")


def main():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('localhost', 2002))
    s.listen(5)

    while True:
        print("server running on localhost port number 2002")
        print("server listening..")
        c, addr = s.accept()
        print('Got connection from', addr)
        start_new_thread(new_client, (c, addr))
    s.close()
    sys.exit()


main()
