#!/usr/bin/env python3

import socket
import sys

# python3.8 fileget.py -n 147.229.8.12:3333 -f fsp://foo.bar/file.txt

if len(sys.argv) != 5:
    sys.stderr.write("Nespravny pocet parametru!")
    exit(1)
else:
    if sys.argv[1] == "-f":
        if sys.argv[2][:6] != "fsp://":
            sys.stderr.write("Nespravny tvar parametru!")
            exit(1)
        else:
            fsp = sys.argv[2][6:]
            if sys.argv[3] == "-n":
                ip_adress = sys.argv[4]
            else:
                sys.stderr.write("Nespravny tvar parametru!")
                exit(1)
    elif sys.argv[1] == "-n":
        ip_adress = sys.argv[2]
        if sys.argv[3] == "-f":
            if sys.argv[4][:6] != "fsp://":
                sys.stderr.write("Nespravny tvar parametru!")
                exit(1)
            else:
                fsp = sys.argv[4][6:]
        else:
            sys.stderr.write("Nespravny tvar parametru!")
            exit(1)
    else:
        sys.stderr.write("Nespravny typ parametru!")
        exit(1)

    #       UDP        #
download_all = False
host = ip_adress.split(":")[0]
port = int(ip_adress.split(":")[-1])
FTD = fsp.split("/")
file_to_download = ""
website = fsp.split("/")[0]
x = 1
while x < len(FTD):
    file_to_download = file_to_download + FTD[x]
    x = x + 1
if file_to_download == "*":
    download_all = True
    file_to_download = "index"
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.sendto(bytes("WHEREIS " + str(website), "utf-8"), (host, port))
try:
    msg = s.recv(1024)
    msg = msg.decode("utf-8")
except:
    sys.stderr.write("Zprava nedorucena!")
    exit(1)
if msg[:2] == "OK":
    pass
    host = msg.split(":")[0].split(" ")[-1]
    port = msg.split(":")[-1]
else:
    sys.stderr.write("Server nenalezen!")
    exit(1)
s.close()

    #       TCP       #
already_download = []
def download_file(file_to_download, website):
    global already_download
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((str(host), int(port)))
    s.send(("GET " + file_to_download + " FSP/1.0\nHostname: " + website + "\n" + "Agent: xdobes21\n\n").encode("utf-8"))
    try:
        msg = s.recv(1024)
        decoded = msg.decode("utf-8")
    except:
        sys.stderr.write("Zprava neobdrzena!")
        exit(1)
    first_line = decoded.split("\n")[0]
    if first_line == "FSP/1.0 Success\r":
        second_line = decoded.split("\n")[1]
        #Length = int(second_line.split(":")[-1])
    else:
        sys.stderr.write("Soubor neobdrzen!")
        exit(1)
    new_name = file_to_download.split("/")[-1]
    counter = 0
    for name in already_download:
        if name == new_name:
            counter = counter + 1
            nahme = new_name.split(".")[0]
            new_name = nahme + " (" + str(counter) + ")." + new_name.split(".")[-1]
    already_download.append(new_name)
    file = open(new_name, "wb")
    text = decoded.split(second_line)[-1]
    msg = msg[len(first_line) + len(second_line)+4:]
    file.write(msg)
    msg = "b's'"
    while str(msg) != "b''":
        try:
            msg = s.recv(1024)
            file.write(msg)
        except:
            break
    file.close()
    s.close()
    print("File "+ str(file_to_download.split("/")[-1]) + " has been successfully downloaded.")
if download_all == False:
    download_file(file_to_download, website)
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((str(host), int(port)))
    s.send(("GET index FSP/1.0\nHostname: " + website + "\n" + "Agent: xdobes21\n\n").encode("utf-8"))
    try:
        msg = s.recv(1024)
        msg = msg.decode("utf-8")
    except:
        sys.stderr.write("Zprava neobdrzena!")
        exit(1)
    first_line = msg.split("\n")[0]
    if first_line == "FSP/1.0 Success\r":
        second_line = msg.split("\n")[1]
    else:
        sys.stderr.write("Soubor neobdrzen!")
        exit(1)
    text = msg.split(second_line)[-1]
    #text = text.split("\n")
    files = ""
    while text != "":
        files = files + str(text)
        try:
            msg = s.recv(1024)
            text = msg.decode("utf-8")
        except:
            break
    files = files.split("\n")
    s.close()
    for file in files:
        if len(file) >= 4:
            if file[-1] == "\r":
                file = file.split("\r")[0]
            download_file(file, website)