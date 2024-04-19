import os
import mimetypes
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.events import StreamDataReceived
from aioquic.h3.connection import H3_ALPN, H3Connection
from aioquic.h3.events import HeadersReceived, DataReceived
import argparse
import contextlib
import os
import os.path
from  http import HTTPStatus
import http.server as hs
import logging
import shutil
import socket
import sys
import threading
import asyncio
import os
from aioquic.asyncio import serve
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.h3.connection import H3Connection
from aioquic.h3.events import DataReceived, HeadersReceived, H3Event
import aiofiles 
import asyncio


class HTTPChunkedRequestReader:

    _stream = None
    _eof    = False

    _logger = None

    def __init__(self, stream, logger):
        self._stream = stream
        self._logger = logger

    def read(self):
        if self._eof:
            return bytes()

        l = self._stream.readline().decode('ascii', errors = 'replace')
        self._logger.debug('reading chunk: chunksize %s', l)

        try:
            chunk_size = int(l.split(';')[0], 16)
        except ValueError:
            raise IOError('Invalid chunksize line: %s' % l)
        if chunk_size < 0:
            raise IOError('Invalid negative chunksize: %d' % chunk_size)
        if chunk_size == 0:
            self._eof = True
            return bytes()

        data      = bytes()
        remainder = chunk_size
        while remainder > 0:
            read = self._stream.read(remainder)
            if len(read) == 0:
                raise IOError('Premature EOF')

            data      += read
            remainder -= len(read)

        term_line = self._stream.readline().decode('ascii', errors = 'replace')
        if term_line != '\r\n':
            raise IOError('Invalid chunk terminator: %s' % term_line)

        return data

class HTTPRequestReader:

    _stream    = None
    _remainder = 0
    _eof       = False

    def __init__(self, stream, request_size):
        self._stream    = stream
        self._remainder = request_size
        self._eof       = request_size == 0

    def read(self):
        if self._eof:
            return bytes()

        read = self._stream.read1(self._remainder)
        if len(read) == 0:
            raise IOError('Premature EOF')

        self._remainder -= len(read)
        self._eof        = self._remainder <= 0

        return read

class DataStream:

    _data      = None
    _data_cond = None
    _eof       = False

    def __init__(self):
        self._data      = []
        self._data_cond = threading.Condition()

    def close(self):
        with self._data_cond:
            self._eof = True
            self._data_cond.notify_all()

    def write(self, data):
        with self._data_cond:
            if len(data) == 0:
                self._eof = True
            else:
                if self._eof:
                    raise ValueError('Tried to write data after EOF')

                self._data.append(data)

            self._data_cond.notify_all()

    def read(self, chunk):
        with self._data_cond:
            while self._eof is False and chunk >= len(self._data):
                self._data_cond.wait()

            if chunk < len(self._data):
                return self._data[chunk]

            return bytes()

class StreamCache:

    _streams = None
    _lock    = None
    _logger  = None

    def __init__(self, logger):
        self._streams = {}
        self._lock    = threading.Lock()
        self._logger  = logger

    def __getitem__(self, key):
        self._logger.debug('reading from cache: %s', key)
        with self._lock:
            return self._streams[key]

    @contextlib.contextmanager
    def add_entry(self, key, val):
        self._logger.debug('cache add: %s', key)
        with self._lock:
            if key in self._streams:
                raise ValueError('Duplicate cache entry: %s' % key)
            self._streams[key] = val
        try:
            yield val
        finally:
            with self._lock:
                del self._streams[key]
            self._logger.debug('cache delete: %s', key)

class DashRequestHandler(hs.BaseHTTPRequestHandler):
    # required for chunked transfer
    protocol_version = "HTTP/1.1"

    _logger = None

    def __init__(self, *args, **kwargs):
        server = args[2]
        self._logger = server._logger.getChild('requesthandler')

        super().__init__(*args, **kwargs)

    def _decode_path(self, encoded_path):
        # FIXME implement unquoting
        return encoded_path

    def _serve_local(self, path):
        with open(path, 'rb') as infile:
            stat = os.fstat(infile.fileno())

            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Length', str(stat.st_size))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            shutil.copyfileobj(infile, self.wfile)

    def _log_request(self):
        self._logger.info('%s: %s', str(self.client_address), self.requestline)
        self._logger.debug('headers:\n%s', self.headers)

    def do_POST(self):
        self._log_request()

        with contextlib.ExitStack() as stack:
            local_path = self._decode_path(self.path)

            ds = stack.enter_context(contextlib.closing(DataStream()))
            stack.enter_context(self.server._streams.add_entry(local_path, ds))

            if 'Transfer-Encoding' in self.headers:
                if self.headers['Transfer-Encoding'] != 'chunked':
                    return self.send_error(HTTPStatus.NOT_IMPLEMENTED,
                                            'Unsupported Transfer-Encoding: %s' %
                                            self.headers['Transfer-Encoding'])
                infile = HTTPChunkedRequestReader(self.rfile, self._logger.getChild('chreader'))
            elif 'Content-Length' in self.headers:
                infile = HTTPRequestReader(self.rfile, int(self.headers['Content-Length']))
            else:
                return self.send_error(HTTPStatus.BAD_REQUEST)

            outpath    = '%s%s' % (self.server.serve_dir, local_path)
            write_path = outpath + '.tmp'
            outfile    = stack.enter_context(open(write_path, 'wb'))
            while True:
                data = infile.read()

                ds.write(data)
                if len(data) == 0:
                    self._logger.debug('Finished reading')
                    break

                written = outfile.write(data)
                if written < len(data):
                    raise IOError('partial write: %d < %d' % (written, len(data)))

                self._logger.debug('streamed %d bytes', len(data))

            retcode = HTTPStatus.NO_CONTENT if os.path.exists(outpath) else HTTPStatus.CREATED
            os.replace(write_path, outpath)

        self.send_response(retcode)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_PUT(self):
        return self.do_POST()            

class DashQUICServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._http = H3Connection(self._quic)

    def _decode_path(self, encoded_path):
        # FIXME implement unquoting
        return encoded_path

    def quic_event_received(self, event):
        if isinstance(event, H3Event):
            self.handle_http_event(event)

    async def _serve_local(self, stream_id, path):
        # 使用aiofiles异步打开文件
        async with aiofiles.open(path, 'rb') as infile:
            # 获取文件状态信息以读取文件大小
            stat = await infile.stat()

            # 发送HTTP响应头部
            self._http.send_headers(
                stream_id=stream_id,
                headers=[
                    (b":status", b"200"),
                    (b"content-length", str(stat.st_size).encode()),
                    (b"access-control-allow-origin", b"*")
                ],
                end_stream=False
            )

            # 异步读取文件并发送内容
            while True:
                data = await infile.read(65536)  # 以块的方式读取，例如每块65536字节
                if not data:
                    break
                self._http.send_data(stream_id=stream_id, data=data, end_stream=False)
            # 完成文件传输
            self._http.send_data(stream_id=stream_id, data=b'', end_stream=True)  
        
    def _log_request(self):
        self._logger.info('%s: %s', str(self.client_address), self.requestline)
        self._logger.debug('headers:\n%s', self.headers)       

    async def handle_http_event(self, event):
        if isinstance(event, HeadersReceived):
            # Determine the request method and path
            method = path = None
            for header, value in event.headers:
                if header == b":method":
                    method = value.decode()
                elif header == b":path":
                    path = value.decode()
            if method == "GET":
                await self.handle_get_request(event.stream_id, path)
        elif isinstance(event, DataReceived):
            # Handle incoming data (not used in GET)
            pass
    

    async def handle_get_request(self, stream_id, path):
        self._log_request()

        local_path = self._decode_path(self.path)  # 解码请求的路径

        outpath = '%s/%s' % ("/home/streaming/dash-ll-server-aioquic/media", local_path)
        if os.path.exists(outpath):  # 检查文件是否存在
            self._logger.info('serve local: %s', local_path)  # 记录服务本地文件的日志
            return self._serve_local(outpath)  # 服务本地文件
        else:
            self._http.send_headers(
            stream_id=stream_id,
            headers=[(b":status", b"404"), (b"server", b"aioquic")],
            end_stream=True
        )  # 文件不存在时发送404错误
            return




class DashServer(hs.ThreadingHTTPServer):

    serve_dir = None

    # files currently being uploaded, indexed by their URL
    # should only be accessed by the request instances spawned by this server
    _streams = None

    _logger  = None

    def __init__(self, address, force_v4, force_v6, serve_dir, logger):
        self.serve_dir     = serve_dir
        self._streams      = StreamCache(logger.getChild('streamcache'))
        self._logger       = logger

        family = None
        if force_v4:
            family = socket.AF_INET
        elif force_v6:
            family = socket.AF_INET6

        if family is None and len(address[0]):
            try:
                family, _, _, _, _ = socket.getaddrinfo(*address)[0]
            except IndexError:
                pass

        if family is None:
            family = socket.AF_INET6

        self.address_family = family

        super().__init__(address, DashRequestHandler)

# class Http3ServerProtocol(QuicConnectionProtocol):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.http = H3Connection(self._quic)

#     def quic_event_received(self, event):
#         if isinstance(event, StreamDataReceived):
#             self.http.handle_event(event)
#         if isinstance(event, HeadersReceived):
#             self.handle_request(event)

#     def handle_request(self, event):
#         method, path, headers, _ = event.headers
#         response_headers = [(b"server", b"aiodemo/0.1")]
#         if method == b"GET":
#             content_path = os.path.join("path_to_content", path.decode())
#             if os.path.exists("./media"):
#                 content_type, _ = mimetypes.guess_type(content_path)
#                 with open(content_path, 'rb') as file:
#                     response_headers.extend([
#                         (b"content-type", content_type.encode()),
#                         (b"status", b"200")
#                     ])
#                     data = file.read()
#                     self.http.send_headers(event.stream_id, response_headers, end_stream=False)
#                     self.http.send_data(event.stream_id, data, end_stream=True)
#             else:
#                 response_headers.append((b"status", b"404"))
#                 self.http.send_headers(event.stream_id, response_headers, end_stream=True)

async def run_server():
    configuration = QuicConfiguration(is_client=False, alpn_protocols=H3_ALPN)
    configuration.load_cert_chain('/home/streaming/dash-ll-server-aioquic/cert.pem', '/home/streaming/dash-ll-server-aioquic/key.pem')
    serverawait = serve('0.0.0.0', 9000, configuration=configuration, create_protocol=DashQUICServerProtocol)
        # 保持服务器运行
    try:
        await asyncio.Future()  # 永远等待直到有取消或异常发生
    finally:
        server.close()
        await server.wait_closed()



def main(argv):
    parser = argparse.ArgumentParser('DASH server')

    parser.add_argument('-a', '--address', default = '0.0.0.0')
    parser.add_argument('-p', '--port',    type = int, default = 9001)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-4', '--ipv4',    action = 'store_true')
    group.add_argument('-6', '--ipv6',    action = 'store_true')

    parser.add_argument('-l', '--loglevel', default = 'WARNING')

    parser.add_argument('directory')

    args = parser.parse_args(argv[1:])

    logging.basicConfig(stream = sys.stderr, level = args.loglevel)
    logger = logging.getLogger('DashServer')

    server = DashServer((args.address, args.port), args.ipv4, args.ipv6,
                        'media', logger)
    server.serve_forever()

    asyncio.run(run_server())

if __name__ == '__main__':
    main(sys.argv)
