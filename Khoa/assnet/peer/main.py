import os
import sys
import threading
import torrent 
from client import client
import constant
import bencodepy
from server import server
from threading import Thread

    
if __name__ == "__main__":
   
    peer_ip = server.get_host_default_interface_ip()
    server_port = 8080

    stop_event = threading.Event()

    peer_server = Thread(target=server.start_server, args=(peer_ip,server_port,stop_event))
    peer_server.start()

    peer_id = server.generate_peer_id_with_ip("-MStat-",peer_ip)

    while True:
        command_line = input("\n> ").strip()

        if command_line.startswith("menu"):
            print("Torrent App")
            print("Commands Available:")
            print("     create [tracker-url] [files]")
            print("     seed [your torrent file]")
            print("     getlistofpeers [your torrent file]")
            print("     getTracker")
            print("     download [your torrent file]")
            print("     share")
            print("     exit")

        elif command_line.startswith("getTracker"):
            
            tracker_address = '192.168.56.1:8080'
            # tracker = client.AnnounceToTracker( peer_address, filename)
            print("No trackers connected.")
        
        elif command_line.startswith("share"):
            print("started sharing...")

        elif command_line.startswith("seed"):
            torrent_file = command_line.split(" ")[1]
            client.Seed(peer_id,peer_ip,torrent_file)

        elif command_line.startswith("create"):
            tracker_url = f"http://{command_line.split(' ')[1]}:4000"
            client.connected_tracker_addresses.append(tracker_url)
            filepath = command_line.split(' ')[2:]
            torrent.Create(filepath,tracker_url)
            # print("started create...")

        elif command_line.startswith("download"):
            torrent_file = command_line.split(" ")[1]
            client.Download(peer_id,peer_ip,torrent_file)

        elif command_line.startswith("exit"):
            print("Shutting down...")
            client.disconnect_to_tracker(peer_id,peer_ip)
            stop_event.set()
            peer_server.join()
            sys.exit()

    