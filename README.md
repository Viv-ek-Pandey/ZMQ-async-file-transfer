Setup
Client Configuration

Edit client/config.yaml:

broker_tcp_address: "tcp://<BROKER_IP>:<PORT>"
Replace <BROKER_IP> and <PORT> with the broker's IP and port.

Worker Configuration

Edit the server and client config.yaml:
number_of_workers: <NUM_WORKERS>

Replace <NUM_WORKERS> with the number of server and client workers you want to start.

How it Works

Client Worker:
Starts with IDs: 1, 2, 3, …
Each client expects files: file1.txt, file2.txt, …
Sends these files to the broker for processing.

Server Worker:
Starts with IDs: 1, 2, 3, 4, …
Receives files from the broker.
Creates output files: Test1.txt, Test2.txt, …

Broker:
Routes messages between clients and server workers.
Ensures that files sent by clients are received by the server workers.

Notes:
    Worker IDs are automatically assigned starting from 1.
    Ensure the server is running before starting client.
    File names expected by clients must match the names specified (file1.txt, file2.txt, …).