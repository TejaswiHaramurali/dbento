import socket;
import random;
import pandas as pd;
import time;
import sys;
from argparse import ArgumentParser;
import traceback;
import select;
import logging;


def ProcessMessage(msg, GroupMap, df):
    logging.debug("  Current state of the datframe.");
    logging.debug(df);
    timestamp = int(time.time());
    rowlist = [];
    rowmap = {};
    msgstr = msg.decode('utf-8');
    if msgstr == '' or len(msgstr) != 1:
        logging.error("  Received invalid input." + str(msg));
        return;
    partition = GroupMap.get(msgstr[0], None);
    if partition is None:
        logging.error("  Unable to find symbol " + str(msgstr[0]));
        return;
    rowmap['Timestamp'] = timestamp;
    rowmap['Symbol'] = msgstr[0];
    rowmap['Group'] = partition;
    rowlist.append(rowmap);
    if df.empty:
        df = df.append(rowlist);
    else:
        if (df.iloc[0])['Timestamp'] == timestamp:
            df = df.append(rowlist);
            logging.debug("  Current status of Messages vs partitions they belong to.")
            logging.debug(df['Group'].value_counts());
            valuemap = df['Group'].value_counts();
            values = (valuemap.to_dict()).values();
            if max(values) > 3:
                logging.critical("  TRADING VIOLATION ALERT.");
                sys.exit();
        else:
            df = df[0:0];
            df = df.append(rowlist);
    return df;
            

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

    if args.rate_limit <= 0:
        logging.error("  Maximum limit of messages per sec cannot be zero or negative.");
        sys.exit();

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
            readable, writable, exceptional = select.select(inputs, [], []);
            data = conn.recv(1028);
            if data is None or len(data) == 0:
                continue;
            else:
                ## <TEJ> Validata data here##
                df = ProcessMessage(data, group_map, df);
    except Exception as e:
        logging.error("  Exception occurred.");
        traceback.print_exc();


if __name__ == "__main__":
    main();
