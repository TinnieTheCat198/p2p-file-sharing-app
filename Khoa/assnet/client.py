import socket
import struct
import threading
import hashlib
import json

connected_tracker_addresses = []

class AddrAndFilename:
    def __init__(self, addr, filename):
        self.addr = addr
        self.filename = filename

class PieceWork:
    def __init__(self, index, hash, size):
        self.index = index
        self.hash = hash
        self.size = size

class PieceResult:
    def __init__(self, index, data, error):
        self.index = index
        self.data = data
        self.error = error

# def start_download(torrent_file, another_peer_addresses, peer_address):
#     print(f"Starting download for: {torrent_file}")

#     tfs = torrent.open_torrent(f"torrent_files/{torrent_file}")
#     if not tfs:
#         print("Error opening torrent file.")
#         return

#     active_peers = []
#     for peer in another_peer_addresses:
#         print(f"Testing connection to peer: {peer}")
#         if test_connection(peer):
#             print(f"Peer {peer} is available")
#             if perform_handshake(peer, tfs[0]["InfoHash"]):
#                 active_peers.append(peer)
#         else:
#             print(f"Peer {peer} is not available.")

#     if not active_peers:
#         print("No available active peers found!")
#         return

#     for tf in tfs:
#         print(f"Downloading file: {tf['Name']}")
#         num_workers = 3
#         work_queue = [PieceWork(i, h, tf["PieceLength"]) for i, h in enumerate(tf["PieceHashes"])]
#         results = []

#         threads = []
#         for i in range(num_workers):
#             peer = active_peers[i % len(active_peers)]
#             thread = threading.Thread(target=download_worker, args=(peer, work_queue, results, tf["InfoHash"]))
#             thread.start()
#             threads.append(thread)

#         for thread in threads:
#             thread.join()

#         pieces_by_index = {result.index: result.data for result in results if not result.error}
#         for result in results:
#             if result.error:
#                 print(f"Error downloading piece {result.index}: {result.error}")
#             else:
#                 calculated_hash = hashlib.sha1(result.data).digest()
#                 if calculated_hash != tf["PieceHashes"][result.index]:
#                     print(f"Piece {result.index} hash mismatch!")
#                 else:
#                     print(f"Successfully downloaded piece {result.index} of {tf['Name']}")

#         if torrent.merge_pieces(tf["Name"], pieces_by_index):
#             print(f"Download complete for file: {tf['Name']}")
#             tracker_address = tf["Announce"]
#             torrent.create([tf["Name"]], tracker_address)
#             connect_to_tracker(tracker_address, peer_address, tf["Name"])
#         else:
#             print(f"Error merging pieces for {tf['Name']}.")

#     print("All downloads complete!")

def download_worker(peer, work_queue, results, info_hash):
    while work_queue:
        piece = work_queue.pop(0)
        print(f"Downloading piece {piece.index} from peer {peer}")
        data, error = request_piece_from_peer(peer, piece.index, info_hash)
        results.append(PieceResult(piece.index, data, error))

def request_piece_from_peer(address, piece_index, info_hash):
    try:
        with socket.create_connection((address.split(":")[0], int(address.split(":")[1])), timeout=60) as conn:
            perform_handshake(address, info_hash)
            message = f"Requesting:{info_hash.hex()}:{piece_index}\n".encode()
            conn.sendall(message)

            size_header = conn.recv(8)
            piece_size = struct.unpack(">Q", size_header)[0]

            data = conn.recv(piece_size)
            return data, None
    except Exception as e:
        return None, str(e)

def test_connection(address):
    try:
        with socket.create_connection((address.split(":")[0], int(address.split(":")[1])), timeout=5) as conn:
            conn.sendall(b"test:\n")
            response = conn.recv(1024).decode()
            print(f"Received response: {response}")
            return True
    except Exception as e:
        print(f"Test connection failed: {e}")
        return False

def perform_handshake(address, info_hash):
    try:
        with socket.create_connection((address.split(":")[0], int(address.split(":")[1])), timeout=5) as conn:
            handshake_msg = f"HANDSHAKE:{info_hash.hex()}\n".encode()
            conn.sendall(handshake_msg)
            response = conn.recv(1024).decode()
            return response.strip() == "OK"
    except Exception as e:
        print(f"Handshake failed: {e}")
        return False

def connect_to_tracker(tracker_address, peer_address, filename):
    try:
        with socket.create_connection((tracker_address.split(":")[0], int(tracker_address.split(":")[1]))) as conn:
            message = f"START:{peer_address}:{filename}\n".encode()
            conn.sendall(message)
            print(f"Connected to tracker {tracker_address} for file {filename}")
    except Exception as e:
        print(f"Connection to tracker failed: {e}")

# Remaining functions like `disconnect_to_tracker` and `get_list_of_peers` can be implemented similarly.
