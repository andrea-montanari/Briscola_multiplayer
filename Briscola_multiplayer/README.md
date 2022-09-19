# Briscola multiplayer
Gioco della Briscola multiplayer.
Supporta due giocatori per partita.

## Struttura
Client: gestisce la logica di gioco, l'interfaccia grafica e comunica col server per creare nuove partite, unirsi a partite esistenti e per ottenere le carte giocate dall'avversario e per pescare. Ogni giocatore deve eseguire un'istanza Client.

Server: gestisce la creazione e l'eliminazione delle partite e la comunicazione tra i giocatori.

## Prerequisiti
* [python 3.8 o superiore](https://www.python.org/downloads/)
* pipenv
<br>
installazione:
  ```
  $ pip3 install pipenv
  ```

  
## Librerie non standard utilizzate
* Pyro5
* Pygame

Per installare le librerie posizionarsi nella cartella del progetto ed eseguire da terminale:
```
$ pipenv install
```
Nota: l'installazione delle librerie è necessaria sia sulla macchina adibita a server sia sui client.

## Attivazione nameserver
Sulla macchina che si vuole adibire a server, aprire un terminale nella cartella del progetto e digitare:
```
pipenv shell
python -m Pyro5.nameserver --host <host_ip> -p <port>
```

Sostituire a \<host_ip> l'indirizzo IP della macchina su cui si sta eseguendo e a \<port> una porta libera tramite la quale si darà accesso al nameserver (inserire 0 per far scegliere la porta automaticamente).

## Esecuzione server
Sulla macchina che si vuole adibire a server, aprire un terminale nella cartella del progetto e digitare:
```
pipenv shell
python Server.py
```

## Configurazione Client
All'interno della cartella del progetto inserire un file con nome 'remote_connection_config.py' e inserirvi un dizionario Python con la seguente struttura:
```
server_address = {
    "ip": <indirizzo ip del nameserver>,
    "port": <porta utilizzata dal nameserver>
}
```
sostituendo \<indirizzo ip del nameserver> e \<porta utilizzata dal nameserver> con ip e porta assegnati precedentemente al nameserver.

## Esecuzione Client
Posizionarsi nella cartella del progetto ed eseguire da terminale:
```
pipenv shell
python Client.py
```

## Note
Sostituire "py" a "python" in tutti i comandi indicati sopra nel caso in cui il comando "python" non dovesse funzionare.

Il sistema è attualmente funzionante solamente in reti locali.