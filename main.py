"""
This script is licensed under the MIT License and is 
copyrighted by Sebastian Friedl in 2023.

The script is designed to download files from different protocols including HTTP,
FTP, OPC UA, and SMB. It measures the time taken to download files of different sizes
(1MB, 100MB, and 1GB) from each protocol and writes the results to a CSV file.
"""

# Importing necessary libraries
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

# Configuration parameters
# Configuration parameters
download_folder = "download/"  # The directory where the downloaded files are stored
http_url = "http://your-http-server-url/webalizer/"  # The URL for HTTP downloads
ftp_url =  "your-ftp-server-url"  # The URL for FTP downloads
ftp_user = "your-ftp-username"  # The username for FTP downloads
ftp_password = "your-ftp-password"  # The password for FTP downloads
opcua_url = "opc.tcp://your-opcua-server-url:4840"  # The URL for OPC UA downloads
smb_base_path = r'\\your-smb-server-ip\smb_volumen\\'  # The base path for SMB downloads

# Caching the hash of the test file
@functools.lru_cache()
def get_test_hash(test_file):
    return get_file_hash(test_file)

# Function to get the MD5 hash of a file
def get_file_hash(file : str ):
    md5 = hashlib.md5()
    BUF_SIZE = 65536  # Reading the file in 64kb chunks
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            md5.update(data)
    return "{0}".format(md5.hexdigest())

# Function to measure the time taken by a function to execute
def function_duration_measurment(func,file):
    start_time = time.time()
    func(file)
    end_time = time.time()
    return end_time - start_time

# Function to test a protocol by downloading a file n times, measure the time taken, and print and write the results to a CSV file
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

# Function to print the test results
def print_result(test_name, max_time, min_time, all_time, count):
    print(test_name)
    print(f"Count: {count}")
    print(f"Max Time: {max_time}")
    print(f"Min Time: {min_time}")
    print(f"Mean Time: {all_time / count}")

# Function to write the test results to a CSV file
def write_to_result_csv(test_name, file, n, max_time, min_time, all_time, count):
    with open('results.csv','a', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        writer.writerow([test_name,file,"count",n])
        writer.writerow(["Resultqoute", count/n])
        writer.writerow(["Max Time",max_time])
        writer.writerow(["Min Time",min_time])
        writer.writerow(["Mean Time",all_time / count])

# Function to download a file using HTTP and check its integrity
def http_download(file):
    response = requests.post(http_url + file)
    if response.ok :
        with open(download_folder + "http.data", 'wb') as fp:
            fp.write(response.content)
        if not (get_file_hash(download_folder + "http.data") == get_test_hash(file)):
            raise Exception("HTTP file was not correct")
    else:
         raise Exception("HTTP file was not correct")

# Function to download a file using FTP and check its integrity
def ftp_download(file):
    ftp = ftplib.FTP(ftp_url,user=ftp_user,passwd=ftp_password)
    ftp.login(user=ftp_user,passwd=ftp_password)
    with open(download_folder + "ftp.data", 'wb') as fp:
        ftp.retrbinary("RETR {}".format(file),fp.write)
    if not (get_file_hash(download_folder + "ftp.data") == get_test_hash(file)):
        raise Exception("FTP file was not correct")

# Function to download a file using OPC UA and check its integrity
def opcua_download(file):
    asyncio.run(opcua_download_async(file))

# Async function to download a file using OPC UA and check its integrity
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
        if not (get_file_hash(download_folder + "opcua.data") == get_test_hash(file)):
            raise Exception("HTTP file was not correct")

# Function to download a file using SMB and check its integrity
def smb_download(file):
    with open(smb_base_path + file, 'rb') as reomte_file:
        with open(download_folder + "smb.data", 'wb') as local_file:
            local_file.write(reomte_file.read())     
    if not (get_file_hash(download_folder + "smb.data") == get_test_hash(file)):
        raise Exception("smb file was not correct")

# Creating a directory for downloads if it doesn't exist
path = Path(download_folder)
path.mkdir(parents=True, exist_ok=True)

# Removing any existing files in the download directory
for file in os.scandir(download_folder):
    os.remove(file.path)

# Running the tests for each file size and each protocol
tests = ['test_1m.data','test_100m.data','test_1000m.data'] 
print("Test is running")
for test_file in tests:
    print (test_file, get_test_hash(test_file))
    test_protcol(http_download,"HTTP Download Test",test_file,3)
    test_protcol(ftp_download,"FTP Download Test",test_file,3)
    test_protcol(opcua_download,"OPC UA Download Test",test_file,3)
    test_protcol(smb_download,"SMB Download Test",test_file,3)

