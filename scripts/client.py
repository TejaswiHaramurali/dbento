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

        ## Failure test cases (sending rate_limit+1 msgs within one sec) ##
        for i in range(0, (args.rate_limit+1)):
            sock.send(b"A");
            data = sock.recv(1028);

        time.sleep(1.5);
        
        for i in range(0, (args.rate_limit+1)):
            sock.send(b"E");
            data = sock.recv(1028);

        time.sleep(1.5);

        for i in range(0, (args.rate_limit+1)):
            sock.send(b"K");
            data = sock.recv(1028);

        time.sleep(1.5);

        for i in range(0, (args.rate_limit+1)):
            sock.send(b"P");
            data = sock.recv(1028);

        time.sleep(1.5);

        for i in range(0, (args.rate_limit+1)):
            sock.send(b"T");
            data = sock.recv(1028);

        time.sleep(1.5);

        for i in range(0, (args.rate_limit+1)):
            sock.send(b"Y");
            data = sock.recv(1028);

        time.sleep(1.5);
        sock.close();

    except Exception as e:
        print("\nALERT: Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
