import socket;
import random;
import pandas as pd;
import time;
import sys;
from argparse import ArgumentParser;
import traceback;


def ProcessMessage(msg, GroupMap, df):
    print(df);
    timestamp = int(time.time());
    rowlist = [];
    rowmap = {};
    partition = GroupMap.get(msg, None);
    if partition is None:
        print("ERROR: Unable to find symbol " + str(msg));
        return;
    rowmap['Timestamp'] = timestamp;
    rowmap['Symbol'] = msg;
    rowmap['Group'] = partition;
    rowlist.append(rowmap);
    if df.empty:
        df = df.append(rowlist);
    else:
        if (df.iloc[0])['Timestamp'] == timestamp:
            df = df.append(rowlist);
            print(df['Group'].value_counts());
            valuemap = df['Group'].value_counts();
            values = (valuemap.to_dict()).values();
            if max(values) > 3:
                print("\nERROR: TRADING VIOLATION ALERT.");
                sys.exit();
        else:
            df = df[0:0];
            df = df.append(rowlist);
    return df;
            

def PartitionSymbols(num_grps):
    alphabets = [chr(i) for i in range(65, 91)];
    random.shuffle(alphabets);
    print(alphabets);
    groups = [];
    for grp in range(0, num_grps):
        size = random.randint(1, (len(alphabets) - (num_grps-grp-1)));
        print(size);
        group = alphabets[0:size];
        groups.append(group);
        alphabets = alphabets[size:len(alphabets)];
    if len(alphabets) != 0:
        print("\nINFO: leftover alphabets");
        print(alphabets);
        groups[random.randint(0, len(groups)-1)].extend(alphabets);
    print("\nINFO: Groups is");
    print(groups);
    return groups;


def GetGroupMap(groups):
    groupmap = { v:k for k, grp in enumerate(groups) for v in grp };
    return groupmap;


def main():
    parser = ArgumentParser(
        description="Script to simulate an Exchange server accepting messages from a client.")

    parser.add_argument("--partitions",
        help="Number of partitions into which symbols must be split up.", type=int, default=5);

    parser.add_argument("--rate_limit", default=3,
        help="Maximum number of messages from a single partition that is permitted in one second.", type=int);

    parser.add_argument("--ipaddress",
        help="Server IP address on which application must be started.", type=str, default=None);

    parser.add_argument("--port",
        help="Port on which server application must be started.", type=int, default=None);

    args = parser.parser_args();

    if args.ipaddress is None or args.ipaddress == "":
        print("\nERROR: IP address is a mandatory parameter.");
        sys.exit();
    try:
        socket.inet_aton(args.ipaddress);
    
    except socket.error:
        print("\nERROR: Invalid server IP address specified.\n");
        sys.exit();

    if args.port <= 0 or args.port >= 65536:
        print("\nERROR: Invalid port specified..\n");
        sys.exit(); 

    if args.partitions > 26:
        print("\nERROR: Number of partitions cannot be greater than total number of alphabets (26).");
        sys.exit();
    elif args.partitions <= 0:
        print("\nERROR: Number of partitions must be a positive number between (1-26).");
        sys.exit();

    if args.rate_limit <= 0:
        print("\nERROR: Maximum limit of messages per sec cannot be zero or negative.");
        sys.exit();

    groups_list = PartitionSymbols(args.partitions);
    group_map = GetGroupMap(groups_list);
    df = pd.DataFrame(columns=['Timestamp', 'Symbol', 'Group']);

    try:
        print("\nINFO: Waiting for incoming client connection.");
        conn, addr = s.accept();
        print("\nINFO: Incoming client connection from " + str(addr));
        while True:
            data = conn.recv(1028);
            ## <TEJ> Validata data here##
            df = ProcessMessage(data, group_map, df);
    except Exception as e:
        print("\nALERT: Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
