import os
import ssl
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import QuicEvent, StreamDataReceived
from aioquic.tls import SessionTicketHandler

class Http3Server(QuicConnectionProtocol):
    def _log_request(self):
        self._logger.info('%s: %s', str(self.client_address), self.requestline)
        self._logger.debug('headers:\n%s', self.headers)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http_streams = {}

    def quic_event_received(self, event: QuicEvent) -> None:
        if isinstance(event, StreamDataReceived):
            data = event.data.decode()
            print(f"Received data: {data}")
            if event.stream_id not in self._http_streams:
                self.handle_new_request(event.stream_id, data)
            else:
                self.send_stream_data(event.stream_id, data.encode())

    def handle_new_request(self, stream_id, data):
        self._log_request()
        # Simple GET request parser
        lines = data.split("\r\n")
        request_line = lines[0]
        method, path, _ = request_line.split()
        if method == "GET":
            file_path = os.path.join('.', 'media', path.lstrip('/'))
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'rb') as file:
                    content = file.read()
                    headers = f"HTTP/3 200 OK\r\nContent-Length: {len(content)}\r\n\r\n"
                    self.send_stream_data(stream_id, headers.encode() + content)
            else:
                self.send_stream_data(stream_id, b"HTTP/3 404 Not Found\r\n\r\n")
    
    def send_stream_data(self, stream_id, data):
        self._quic.send_stream_data(stream_id, data, end_stream=True)

async def run_http3_server():
    configuration = QuicConfiguration(
        is_client=False,
        alpn_protocols=["h3-29"],
    )

    print("0")

    # Load the certificates
    configuration.load_cert_chain('/home/streaming/dash-ll-server-aioquic/cert.pem', '/home/streaming/dash-ll-server-aioquic/key.pem')
    print("1")
    # Start the server
    server = await serve('0.0.0.0', 4433, configuration=configuration, create_protocol=Http3Server)
    print("Server is running...")
    try:
        # Keep the server running forever
        while True:
            await asyncio.sleep(3600)  # Sleep for an hour before checking again
    except KeyboardInterrupt:
        print("Server is shutting down...")
        server.close()
        await server.wait_closed()

# Run the server
import asyncio
asyncio.run(run_http3_server())
