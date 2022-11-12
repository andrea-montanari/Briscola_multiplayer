# Briscola multiplayer
Multiplayer Briscola game realized with Python.

Supports two players per match.

## Structure
Client: handles the game logic, the graphic interface and communicates with the server to create new matches, join existing matches. The communication with the server is also active during the matches: to get the adversary played cards and to draw. Each player executes a Client's instance.

Server: handles the creation and the elimination of the matches and the communication between the players.

## prerequisites
* [python 3.8 or superior](https://www.python.org/downloads/)
* pipenv
<br>
installation:
  ```
  $ pip3 install pipenv
  ```

  
## Non-standard libraries used
* Pyro5
* Pygame

To install the libraries, move to the project's directory and run the following command from terminal:
```
$ pipenv install
```
Note: the libraries installation is necessary both in the client machine and in the server machine.

## Nameserver activation
A Pyro5 nameserver is used to keep track of the objects in the network more easily.
You should activate a Pyro5 nameserver in the server machine running the following commands on the terminal: 
```
pipenv shell
python -m Pyro5.nameserver --host <host_ip> -p <port>
```

Replace \<host_ip> with the IP address of the current machine and \<port> with a free port through which access to the nameserver will be given (insert 0 to make it choose the port automatically).

## Configuration
In the project directory insert a file with the name 'remote_connection_config.py' and write a dictionary with the following structure in it (or modify the existing one):
```
server_address = {
    "ip": <ip address of the nameserver>,
    "port": <port used by the nameserver>
}
```
replacing \<ip address of the nameserver> and \<port used by the nameserver> with IP and port previously assigned to the nameserver.

Note: this configuration is necessary both in the client machines and in the server machines

## Server execution
In the server machine, open a terminal in the project directory and run:
```
pipenv shell
python Server.py
```

## Client execution
Position in the project directory and run from terminal:
```
pipenv shell
python Client.py
```

## Notes
* Replace "python" with "py" in all the above mentioned command in case the "python" command doesn't work.

* In the server machine it is sufficient to keep the files "Server.py", "remote_connection_config.py" and "Pipfile", while in the client machines all the files are necessary with exception of "Server.py".

* The system is currently only able to work in local networks. 
