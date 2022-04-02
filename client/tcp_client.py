import sys
import socket
import json
import logging
import xmltodict
import ssl
import os
import random
import datetime
import threading

server_address = ('172.16.16.104', 12000)

def make_socket(destination_address='localhost',port=12000):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        #logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        return sock
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def make_secure_socket(destination_address='localhost',port=10000):
    try:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.verify_mode=ssl.CERT_OPTIONAL
        context.load_verify_locations(os.getcwd() + '/domain.crt')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = (destination_address, port)
        #logging.warning(f"connecting to {server_address}")
        sock.connect(server_address)
        secure_socket = context.wrap_socket(sock,server_hostname=destination_address)
        #logging.warning(secure_socket.getpeercert())
        return secure_socket
    except Exception as ee:
        logging.warning(f"error {str(ee)}")

def deserialisasi(s):
    # logging.warning(f"deserialisasi {s.strip()}")
    return json.loads(s)
    

def send_command(command_str,is_secure=False):
    alamat_server = server_address[0]
    port_server = server_address[1]
#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# gunakan fungsi diatas
    if is_secure == True:
        sock = make_secure_socket(alamat_server,port_server)
    else:
        sock = make_socket(alamat_server,port_server)

    #logging.warning(f"connecting to {server_address}")
    try:
        #logging.warning(f"sending message ")
        sock.sendall(command_str.encode())
        # Look for the response, waiting until socket is done (no more data)
        data_received="" #empty string
        while True:
            #socket does not receive all data at once, data comes in part, need to be concatenated at the end of process
            data = sock.recv(16)
            if data:
                #data is not empty, concat with previous content
                data_received += data.decode()
                if "\r\n\r\n" in data_received:
                    break
            else:
                # no more data, stop the process by break
                break
        # at this point, data_received (string) will contain all data coming from the socket
        # to be able to use the data_received as a dict, need to load it using json.loads()
        hasil = deserialisasi(data_received)
        #logging.warning("data received from server:")
        return hasil
    except Exception as ee:
        #logging.warning(f"error during data receiving {str(ee)}")
        return False



def getdatapemain(nomor=0,is_secure=False):
    cmd=f"getdatapemain {nomor}\r\n\r\n"
    hasil = send_command(cmd,is_secure)
    if hasil:
        print(f"nama: {hasil['nama']}, nomor: {hasil['nomor']}, posisi: {hasil['posisi']}")
    else:
        print(f"kegagalan pada data transfer")

def getdata_banyakpemain(total, is_secure=False):
    for request in range(total):
        getdatapemain(random.randint(1, 11), is_secure)

def get_time():
    return datetime.datetime.now()

def get_total_time(start_time, finish_time):
    return finish_time-start_time

def thread_start(thread_count,request_per_thread):
    threads = dict()
    start_time = get_time()
    
    for thread in range(thread_count):
        threads[thread] = threading.Thread(target=getdata_banyakpemain,args=(request_per_thread, True))
        threads[thread].start()

    for thread in range(thread_count):
        threads[thread].join()

    finish_time = get_time()
    print(
        f"Waktu yang diperlukan untuk menjalankan {thread_count} thread adalah {get_total_time(start_time,finish_time)}")


if __name__ == '__main__':
    thread_start(20, 6)