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
import hashlib
import functools
import csv
import glob

# general config
download_folder = "download/"

#http config
http_url = "http://seneca-ii.fritz.box/webalizer/"

#ftp config
ftp_url =  "seneca-ii.fritz.box"
ftp_user = "one"
ftp_password = "1234"

#opc ua config
opcua_url = "opc.tcp://seneca-ii.fritz.box:4840"

#smb
smb_base_path = r'\\192.168.178.23\smb_volumen\\'

@functools.lru_cache()
def get_test_hash(test_file):
    return get_file_hash(test_file)

def get_file_hash( file : str ):
    md5 = hashlib.md5()
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return "{0}".format(md5.hexdigest())

def function_duration_measurment(func,file):
    start_time = time.time()
    func(file)
    end_time = time.time()
    return end_time - start_time

def test_protcol(func,test_name,file,n=10):
    max_time = 0
    min_time = 100000000
    all_time = 0
    count = n
    for i in range(0,n):
        print("{} of {} ".format(i+1,n))
        try:
            time = function_duration_measurment(func,file)
            all_time += time
            min_time = min(min_time,time)
            max_time = max(max_time,time)
        except Exception as ex:
            count -= 1
            print(ex)
    print_result(test_name, max_time, min_time, all_time, count)
    write_to_result_csv(test_name, file, n, max_time, min_time, all_time, count)

def print_result(test_name, max_time, min_time, all_time, count):
    print(test_name)
    print(f"Count: {count}")
    print(f"Max Time: {max_time}")
    print(f"Min Time: {min_time}")
    print(f"Mean Time: {all_time / count}")

def write_to_result_csv(test_name + file, n, max_time, min_time, all_time, count):
    with open('results.csv','a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([test_name,file,"count",n])
        writer.writerow(["Resultqoute", count/n])
        writer.writerow(["Max Time",max_time])
        writer.writerow(["Min Time",min_time])
        writer.writerow(["Mean Time",all_time / count])
        

def http_download(file):
    response = requests.post(http_url + file)
    if response.ok :
        with open(download_folder + "http.data", 'wb') as fp:
            fp.write(response.content)
        #print("Download hash ",get_file_hash(download_folder + "http.data"))
        if not (get_file_hash(download_folder + "http.data") == get_test_hash(file)):
            raise Exception("HTTP file was not correct")
    else:
         raise Exception("HTTP file was not correct")


def ftp_download(file):
    ftp = ftplib.FTP(ftp_url,user=ftp_user,passwd=ftp_password)
    ftp.login(user=ftp_user,passwd=ftp_password)
    with open(download_folder + "ftp.data", 'wb') as fp:
        ftp.retrbinary("RETR {}".format(file),fp.write)
    if not (get_file_hash(download_folder + "ftp.data") == get_test_hash(file)):
        raise Exception("FTP file was not correct")
        
def opcua_download(file):
    asyncio.run(opcua_download_async(file))
 
async def opcua_download_async(file):
    async with Client(url=opcua_url) as client:
        idx = 1 # not nice but help 
        remote_file_node =  await client.nodes.objects.get_child([f"{idx}:{file}"])

        # Read file from server
        remote_file_content = None
        async with UaFile(remote_file_node, OpenFileMode.Read.value) as remote_file:
            with open(download_folder + "opcua.data", 'wb') as fp:
                size = await remote_file.get_size();
                while (fp.tell() <size): 
                    fp.write(await remote_file.read())
        print (get_file_hash(download_folder + "opcua.data"))
        if not (get_file_hash(download_folder + "opcua.data") == get_test_hash(file)):
            raise Exception("HTTP file was not correct")

def smb_download(file):
    with open(smb_base_path + file, 'rb') as reomte_file:
        with open(download_folder + "smb.data", 'wb') as local_file:
            local_file.write(reomte_file.read())     
    if not (get_file_hash(download_folder + "smb.data") == get_test_hash(file)):
        raise Exception("smb file was not correct")

path = Path(download_folder)
path.mkdir(parents=True, exist_ok=True)
for file in os.scandir(download_folder):
    os.remove(file.path)

tests = ['test_1m.data','test_100m.data','test_1000m.data'] 
#tests = ['test_100m.data'] 
print("Test is running")
#smb_download(tests[0])
for test_file in tests:
    print (test_file, get_test_hash(test_file))
    test_protcol(http_download,"HTTP Download Test",test_file,3)
    test_protcol(ftp_download,"FTP Download Test",test_file,3)
    test_protcol(opcua_download,"OPC UA Download Test",test_file,3)
    test_protcol(smb_download,"SMB Download Test",test_file,3)

