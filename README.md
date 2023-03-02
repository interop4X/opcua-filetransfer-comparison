# opcua-filetransfer-comparison
This is a small project ot compare the transmission quality of file transfer via opc ua (with FileType), http, and ftp.

## Detailed Description

coming soon 

## How to use

### Installation
You need to install packages on client side and on a server side. It is suggested to use to seperate computer or a networksimulation to get better results. 

### Installation Client side
On client side you only need some python packages for the main script.
```
    pip install -r requirements.txt
```
### Installation Server side
On the server side you need to install a http server, ftp server and a opc ua server.
You can adapte the main.py script to the path or nodeId of the server.

In this example the following server application and configuration are used:

#### HTTP
As http server the apache2 server as [xampp](https://www.apachefriends.org/download.html) application is used. 

#### FTP
As ftp server the vsftp server as docker container [delfer/alpine-ftp-server](https://github.com/delfer/docker-alpine-ftp-server) is used.

#### OPC UA 
As opc ua server the [eclipse milo sample server](https://github.com/digitalpetri/opc-ua-demo-server) is used.


### Configuration of the test
* copy the test file to the different servers
* open the main.py file add modified the configuration (url, password, ...)
* open the main.py file and modified the opcua_download to your server.

If you use the eclipse milo sample server you don´t need to change the opcua_download method but you need to replace the mainfest.txt file with your test.data

## next Steps
- add smb as protocol
- add security 
- add network simulation like (mininet)
