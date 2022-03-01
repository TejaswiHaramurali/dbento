import socket;
import random;
import pandas as pd;
import time;
import sys;
from argparse import ArgumentParser;
import traceback;


def main():
    parser = ArgumentParser(
        description="Script to simulate a trade client which sends messages to the Exchange server.")

    parser.add_argument("--rate_limit", default=3,
        help="Maximum number of messages from a single partition that is permitted in one second.", type=int);

    parser.add_argument("--ipaddress",
        help="Server IP address to connect to.", type=str, default=None);

    parser.add_argument("--port",
        help="Server port to connect to.", type=int, default=None);

    args = parser.parse_args();

    if args.ipaddress is None or args.ipaddress == "":
        print("\nERROR: IP address is a mandatory parameter.");
        sys.exit();
    try:
        socket.inet_aton(args.ipaddress);
    
    except socket.error:
        print("\nERROR: Invalid server IP address specified.\n");
        sys.exit();

    if args.port <= 0 or args.port >= 65536:
        print("\nERROR: Invalid port specified.\n");
        sys.exit(); 

    if args.rate_limit <= 0:
        print("\nERROR: Maximum limit of messages per sec cannot be zero or negative.");
        sys.exit();

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        print("\nINFO: Initiating connection to exchange server.");
        sock.connect((args.ipaddress, args.port));
        '''
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"B");
        time.sleep(0.1);
        sock.send(b"C");
        time.sleep(0.1);        
        '''
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"A");
        time.sleep(0.1);
        sock.send(b"A");
        time.sleep(0.1);

        sock.send(b"G");
        time.sleep(0.1);
        sock.send(b"J");
        time.sleep(0.1);
        sock.send(b"N");
        time.sleep(0.1);

        sock.send(b"f");
        time.sleep(0.1);
        sock.send(b"");
        time.sleep(0.1);
        sock.send(b"k");
        time.sleep(0.1);

    except Exception as e:
        print("\nALERT: Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
