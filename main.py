import asyncio
import os
from pathlib import Path
from asyncua import Client
from asyncua.client.ua_file_transfer import UaFile, UaDirectory
from asyncua.ua import OpenFileMode
from asyncua.ua import uaerrors
import time
import ftplib
import requests

http_url = "http://seneca-ii.fritz.box/webalizer/test.data"
ftp_url =  "seneca-ii.fritz.box"
ftp_path = "test.data"
ftp_user = "one"
ftp_password = "1234"
opcua_url = "opc.tcp://seneca-ii.fritz.box:4840/milo"
opcua_file_node_id = ""
download_folder = "download/"

def function_duration_measurment(func):
    start_time = time.time()
    func()
    end_time = time.time()
    return end_time - start_time

def test_protcol(func,test_name,n=10):
    max_time = 0
    min_time = 100000000
    all_time = 0
    for i in range(0,n):
        print("{} of {} ".format(i+1,n))
        time = function_duration_measurment(func)
        all_time += time
        min_time = min(min_time,time)
        max_time = max(max_time,time)
    print(test_name)
    print("Max Time: {}",max_time)
    print("Min Time: {}",min_time)
    print("Mean Time: {}",all_time / n)




def http_download():
    response = requests.post(http_url)
    if response.ok :
        with open(download_folder + "http.data", 'wb') as fp:
            fp.write(response.content)
            

def ftp_download():
    ftp = ftplib.FTP(ftp_url,user=ftp_user,passwd=ftp_password)
    ftp.login(user=ftp_user,passwd=ftp_password)
    with open(download_folder + "ftp.data", 'wb') as fp:
        ftp.retrbinary("RETR test.data",fp.write)
        
def opcua_download():
    asyncio.run(opcua_download_async())
 
async def opcua_download_async():
    async with Client(url=opcua_url) as client:
        uri = "urn:eclipse:milo:opcua:server:demo"
        idx = await client.get_namespace_index(uri)
        remote_file_system = await client.nodes.objects.get_child([f"{idx}:Files"])
        remote_file_name = "manifesto.txt"
        remote_file_node = await remote_file_system.get_child([f"{idx}:{remote_file_name}"])

        # Read file from server
        remote_file_content = None
        async with UaFile(remote_file_node, OpenFileMode.Read.value) as remote_file:
            with open(download_folder + "opcua.data", 'wb') as fp:
                fp.write(await remote_file.read(65535*63))
        
    

path = Path(download_folder)
path.mkdir(parents=True, exist_ok=True)
for file in os.scandir(download_folder):
    os.remove(file.path)

test_protcol(http_download,"HTTP Download Test",10)
test_protcol(ftp_download,"FTP Download Test",10)
test_protcol(opcua_download,"OPC UA Download Test",10)