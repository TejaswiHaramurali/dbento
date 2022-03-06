# dbento

### <b>Executing the Server</b> 
  sudo python3.6 scripts/server.py --ipaddress IPADDRESS --port PORT --verbose   (verbose mode is optional for debugging.)
  ```
  Eg:
      sudo python3.6 scripts/server.py --ipaddress 127.0.0.1 --port 5555 --verbose 
  ```
  
### <b>Executing the Client</b>
  sudo python3.6 scripts/client.py --ipaddress IPADDRESS --port PORT

  sudo python3.6 scripts/reverse_engineering_client.py --ipaddress IPADDRESS --port PORT
  ```
  Eg:
      sudo python3.6 scripts/client.py --ipaddress 127.0.0.1 --port 5555
  ```

### <b> Notes </b>

- The file 'reverse_engineering_client.py' is the one that dleas with the bonus section. It tries to reverse engineer the manner in which the server has split up the alphabets into partitions. It does it in the following way

```
Try sending A A A B to the exchange (when the rate limit is 3 per sec)
If this fails, we know that A abd B are in the same partition. Ifnot, they are 
in different partitions.
Assume they are in different partitions. So, the existing group structure that the client knows is [ [A], [B] ]

Now, we try sending A A A C. If this fails, we know that A and C are in the same group. So the new group structure will be [ [A, C], [B] ]

Else, if we dont get a trading violation, we try B B B C. If this fails, the new group structure will be [ [A], [B, C] ] But if it succeeds, we know that C is in a new group, and the new structure will be [ [A], [B], [C] ]

We continue this way for all alphabets, and figure out which partitions they belong to.
```

The server's partitions are stored in <b><i>server_symbols.txt</i></b>, and the client's reverse engineered partitions are stored in <b><i>client_symbols.txt</i></b>.
By comparing them, we know that the client has successfully reverse engineered the partitions.

- The file 'client.py' is a simple client that does not do any reverse engineering. It simply sends a few random messages, and tests the server for response messages.
