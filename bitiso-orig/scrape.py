# Made by ChatGPT with an long run, but the result awsome.
# It's a good base with a Bencode decoder
# It encode the torrent hash , generate a peer_id, craft URL, and decode peers

import requests
import struct
import random
import string
import urllib.parse

def urlencode(info_hash):
    return urllib.parse.quote_plus(bytes.fromhex(info_hash))

def generate_peer_id():
    return '-PC0001-' + ''.join(random.choices(string.ascii_letters + string.digits, k=12))

def decode_peers(peers_binary):
    peers = []
    for i in range(0, len(peers_binary), 6):
        ip = '.'.join(map(str, peers_binary[i:i+4]))
        port = struct.unpack('>H', peers_binary[i+4:i+6])[0]
        peers.append(f"IP: {ip}, Port: {port}")
    return peers

def bdecode(data):
    """Simple Bencode decoder."""
    def decode_next(index):
        if data[index] == ord('d'):
            index += 1
            result = {}
            while data[index] != ord('e'):
                key, index = decode_next(index)
                result[key], index = decode_next(index)
            return result, index + 1
        elif data[index] == ord('l'):
            index += 1
            result = []
            while data[index] != ord('e'):
                value, index = decode_next(index)
                result.append(value)
            return result, index + 1
        elif data[index] == ord('i'):
            index += 1
            end = data.index(ord('e'), index)
            return int(data[index:end]), end + 1
        elif data[index: index + 1].isdigit():
            end = data.index(ord(':'), index)
            length = int(data[index:end])
            index = end + 1
            return data[index:index + length], index + length

    result, _ = decode_next(0)
    return result

def main(tracker_url, raw_hash):
    info_hash = urlencode(raw_hash)
    peer_id = generate_peer_id()
    port = 6881
    uploaded = 0
    downloaded = 0
    left = 0
    compact = 1
    event = 'started'

    request_url = (f"{tracker_url}?info_hash={info_hash}&peer_id={peer_id}&port={port}"
                   f"&uploaded={uploaded}&downloaded={downloaded}&left={left}"
                   f"&compact={compact}&event={event}")

    print(f"INFO_HASH: {info_hash}")
    print(f"PEER_ID: {peer_id}")
    print(f"REQUEST_URL: {request_url}")

    response = requests.get(request_url)
    print("Original Response:")
    print(response.content)

    if response.status_code != 200:
        print(f"Error: Received status code {response.status_code}")
        return

    if b"Invalid Request" in response.content:
        print("Invalid Request received. Check the parameters.")
        return

    try:
        decoded_response = bdecode(response.content)
    except Exception as e:
        print(f"Error decoding response: {e}")
        return

    print("Decoded Response:")
    print(decoded_response)

    if b'peers' in decoded_response:
        peers = decode_peers(decoded_response[b'peers'])
        print("Decoded Peers:")
        for peer in peers:
            print(peer)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python scrape_torrent.py <tracker_url> <info_hash>")
    else:
        tracker_url = sys.argv[1]
        info_hash = sys.argv[2]
        main(tracker_url, info_hash)

