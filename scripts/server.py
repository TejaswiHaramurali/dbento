import socket;
import random;
import pandas as pd;
import time;
import sys;
from argparse import ArgumentParser;
import traceback;
import select;
import logging;
import signal;


def signal_handler(signum, frame):
    if signum == signal.SIGINT:
        logging.info("  Terminating the server program.");
        sys.exit();
    elif signum == signal.SIGPIPE:
        logging.info("  Client closed the connection.");
        sys.exit();


def ProcessMessage(msg, GroupMap, df, rate_limit):
    logging.debug("  Current state of the datframe.");
    logging.debug(df);
    timestamp = int(time.time() * 1000.0);
    rowlist = [];
    rowmap = {};
    retval = -1;
    msgstr = msg.decode('utf-8');
    if msgstr == '' or len(msgstr) != 1:
        logging.error("  Received invalid input." + str(msg));
        return (df, 1);
    partition = GroupMap.get(msgstr[0], None);
    if partition is None:
        logging.error("  Unable to find symbol " + str(msgstr[0]));
        return (df, 1);
    rowmap['Timestamp'] = timestamp;
    rowmap['Symbol'] = msgstr[0];
    rowmap['Group'] = partition;
    #logging.debug("  Timestamp -> " + str(timestamp) + ", Symbol -> " + str(msgstr[0]) + ", Group -> " + str(partition));
    rowlist.append(rowmap);
    if df.empty:
        df = df.append(rowlist);
        retval = 0;
    else:
        if ((df.iloc[0])['Timestamp'] + 1000) >= timestamp:
            df = df.append(rowlist);
            #logging.debug("  Current status of Messages vs partitions they belong to.")
            #logging.debug(df['Group'].value_counts());
            valuemap = df['Group'].value_counts();
            values = (valuemap.to_dict()).values();
            if max(values) > rate_limit:
                logging.critical("  TRADING VIOLATION ALERT.");
                retval = 1;
            else:
                retval = 0;
        else:
            df = df[0:0];
            df = df.append(rowlist);
            retval = 0;
    return (df, retval);
            

def PartitionSymbols(num_grps):
    alphabets = [chr(i) for i in range(65, 91)];
    random.shuffle(alphabets);
    groups = [];
    for grp in range(0, num_grps):
        size = random.randint(1, (len(alphabets) - (num_grps-grp-1)));
        logging.debug("  Size of group " + str(grp) + "-> " + str(size));
        group = alphabets[0:size];
        groups.append(group);
        alphabets = alphabets[size:len(alphabets)];
    if len(alphabets) != 0:
        logging.debug("  Alphabets that are left over.");
        logging.debug(alphabets);
        groups[random.randint(0, len(groups)-1)].extend(alphabets);
    logging.debug("  Symbols have been partitioned into the following groups ");
    logging.debug(groups);
    filehandle = open("server_symbols.txt", "w");
    newgroups = groups[:];
    for newgrp in newgroups:
        newgrp.sort();
    newgroups.sort();
    filehandle.write(str(newgroups));
    filehandle.close();
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

    parser.add_argument("--verbose", action='store_true',
        help="Determines whether debug messages need to be printed..");

    args = parser.parse_args();

    if args.verbose == True:
        logging.basicConfig(level=logging.DEBUG);
    else:
        logging.basicConfig(level=logging.INFO);

    if args.ipaddress is None or args.ipaddress == "":
        logging.error("  IP address is a mandatory parameter.");
        sys.exit();
    try:
        socket.inet_aton(args.ipaddress);
    
    except socket.error:
        logging.error("  Invalid server IP address specified.\n");
        sys.exit();

    if args.port <= 0 or args.port >= 65536:
        logging.error("  Invalid port specified.\n");
        sys.exit(); 

    if args.partitions > 26:
        logging.error("  Number of partitions cannot be greater than total number of alphabets (26).");
        sys.exit();
    elif args.partitions <= 0:
        logging.error("  Number of partitions must be a positive number between (1-26).");
        sys.exit();

    if args.rate_limit <= 0 or args.rate_limit > 200:
        logging.error("  Maximum limit of messages per sec must be in the range 1-200.");
        sys.exit();

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGPIPE, signal_handler);

    groups_list = PartitionSymbols(args.partitions);
    group_map = GetGroupMap(groups_list);
    df = pd.DataFrame(columns=['Timestamp', 'Symbol', 'Group']);

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
        s.bind((args.ipaddress, args.port));
        s.listen(5);
        logging.info("  Waiting for incoming client connection.");
        conn, addr = s.accept();
        logging.info("  Incoming client connection from " + str(addr));
        while True:
            inputs = [];
            inputs.append(conn);
            readable, writable, exceptions = select.select(inputs, [], []);
            if len(readable) == 0:
                logging.error("  Invalid file descriptor returned.");
                conn.close();
                break;
            elif len(exceptions) != 0:
                logging.error("  Socket Closed by client.");
                break;
            conn = readable[0];
            data = conn.recv(1028);
            if data is None or len(data) == 0:
                continue;
            else:
                ## <TEJ> Validata data here##
                (df, retval) = ProcessMessage(data, group_map, df, args.rate_limit);
                conn.send(retval.to_bytes(1, "big"));
    except Exception as e:
        logging.error("  Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
