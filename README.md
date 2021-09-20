# realtime-packet-visualiser

### Intsalling Dependencies
For nodejs:
- npm install

For python:
- pip install requirements.txt

Make a 'logs' folder in root directory


### Components
Server (server.js): running on port specified in file, change if required. Receive information from client cpaturing (realtime_capture.py), and send to plotter (app.js)

Web App (app.js): Connected to server, and plotting the data found.

Packet capture (realtime_capture.py): Connected to server, and captures packets from interface and sends data to server.

### How to run
1. Start server in one terminal: node server.js
2. Start capturing in another terminal: python realtime_capture.py
3. View the plots in browser, where url is: https://localhost:{port}, where port number is the one on which the server is running.

