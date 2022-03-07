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

    if args.rate_limit <= 0 or args.rate_limit > 200:
        print("\nERROR: Maximum limit of messages per sec must be in the range 1-200.");
        sys.exit();

    try:
        partitions = [];
        symbols = [chr(i) for i in range(65, 91)];
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        print("\nINFO: Initiating connection to exchange server.");
        sock.connect((args.ipaddress, args.port));
        for symbol in symbols:
            isFound = False;
            print("INFO: Determining partition for symbol " + str(symbol));
            for partition in partitions:
                if len(partition) == 0:
                    continue;
                else:
                    ch = partition[0];
                    for i in range(0, args.rate_limit):
                        sock.send((str(ch)).encode('utf-8'));
                        data = sock.recv(1028);
                    sock.send((str(symbol)).encode('utf-8'));
                    data = sock.recv(1028);
                    retval = int.from_bytes(data, 'little');
                    if retval == 1:  #symbol is part of this partition.
                        partition.append(symbol);
                        isFound = True;
                        break;
                    else:
                        time.sleep(1.2);
                        continue;
            if isFound == False:
                partitions.append([symbol]);
            time.sleep(2.5);
        filehandle = open("client_symbols.txt", "w");
        filehandle.write(str(partitions));
        filehandle.close(); 
        sock.close();
    except Exception as e:
        print("\nALERT: Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
