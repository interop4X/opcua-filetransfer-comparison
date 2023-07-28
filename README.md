# OPC UA File Transfer Comparison

This project aims to compare the transmission quality of file transfer via different protocols: OPC UA (with FileType), HTTP, and FTP. The comparison is made using a client-server model, where the client retrieves a file from the server using each of the protocols.

## Detailed Description

This project provides a detailed comparison of file transfer protocols. It measures the performance and reliability of OPC UA, HTTP, and FTP in transferring files from a server to a client. The comparison is done under various network conditions to provide a comprehensive analysis. More details will be provided soon.

## How to Use

### Installation

The project requires installations on both the client and server sides. It is recommended to use two separate computers or a network simulation for more accurate results.

### Client Side Installation

On the client side, you need to install some Python packages for the main script. You can do this by running the following command:

```bash
pip install -r requirements.txt
```

### Server Side Installation

On the server side, you need to install an HTTP server, FTP server, and an OPC UA server. You can adapt the `main.py` script to match the path or nodeId of your server.

In this example, the following server applications and configurations are used:

#### HTTP

For the HTTP server, we use the Apache2 server as part of the [XAMPP](https://www.apachefriends.org/download.html) application.

#### FTP

For the FTP server, we use the VSFTP server as a Docker container, specifically [delfer/alpine-ftp-server](https://github.com/delfer/docker-alpine-ftp-server).

#### OPC UA 

see sample node js server (opcua-file-server)(opcua-file-server/README.md)

### Test Configuration

1. Copy the test file to the different servers.
2. Open the `main.py` file and modify the configuration (URL, password, etc.).
3. Modify the `opcua_download` method in the `main.py` file to match your server.

If you're using the custom Node.js OPC UA server, you don't need to change the `opcua_download` method. However, you will need to replace the `manifest.txt` file with your `test.data` file.

## Next Steps

- Add SMB as a protocol.
- Implement security measures.
- Add network simulation (like Mininet).