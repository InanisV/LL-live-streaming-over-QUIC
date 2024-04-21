package main

import (
"bufio"
"flag"
"fmt"
"io"
"log"
"net/http"
"os"
"path/filepath"
"strconv"
"sync"

"github.com/lucas-clemente/quic-go/http3"
)

func main() {
address := flag.String("address", "localhost", "server address")
port := flag.Int("port", 8000, "server port")
directory := flag.String("directory", "", "serve directory")
flag.Parse()

server := &DashServer{
 Address:   *address,
 Port:      *port,
 Directory: *directory,
 Streams:   make(map[string]*DataStream),
}

server.Serve()
}

type DataStream struct {
data     []byte
dataCond *sync.Cond
eof      bool
}

func NewDataStream() *DataStream {
return &DataStream{
data:     make([]byte, 0),
dataCond: sync.NewCond(&sync.Mutex{}),
eof:      false,
}
}

// Write(p []byte) (n int, err error)
func (ds *DataStream) Write(data []byte) (n int, err error) {
ds.dataCond.L.Lock()
defer ds.dataCond.L.Unlock()

if len(data) == 0 {
 ds.eof = true
} else {
 if ds.eof {
  panic("Tried to write data after EOF")
 }
 ds.data = append(ds.data, data...)
}

ds.dataCond.Broadcast()
return 0, nil
}

func (ds *DataStream) Read(chunk int) []byte {
ds.dataCond.L.Lock()
defer ds.dataCond.L.Unlock()

for !ds.eof && chunk >= len(ds.data) {
 ds.dataCond.Wait()
}

if chunk < len(ds.data) {
 return ds.data[chunk:]
}

return nil
}

type StreamCache struct {
streams map[string]*DataStream
lock    *sync.Mutex
}

func NewStreamCache() *StreamCache {
return &StreamCache{
streams: make(map[string]*DataStream),
lock:    &sync.Mutex{},
}
}

type DashServer struct {
Address     string
Port        int
Directory   string
Streams     map[string]*DataStream
StreamCache *StreamCache
}

func (s *DashServer) Serve() {
addr := fmt.Sprintf("%s:%d", s.Address, s.Port)

http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
 path := filepath.Join(s.Directory, r.URL.Path)
 switch r.Method {
 case http.MethodGet:
  s.handleGet(w, r, path)
 case http.MethodPost:
  s.handlePost(w, r, path)
 default:
  http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
 }
})

log.Printf("Server listening on %s\n", addr)
err := http3.ListenAndServe(addr, "example.crt", "example.key", nil)
if err != nil {
 log.Fatalf("Server failed: %v", err)
}
}

func (s *DashServer) handleGet(w http.ResponseWriter, r *http.Request, path string) {
s.logRequest(r)

ds := s.getStreamFromCache(path)
if ds != nil {
 if _, err := os.Stat(path); err == nil {
  s.serveLocalFile(w, path)
 } else {
  http.NotFound(w, r)
 }
 return
}

w.WriteHeader(http.StatusOK)
w.Header().Set("Transfer-Encoding", "chunked")
w.Header().Set("Access-Control-Allow-Origin", "*")
w.Header().Set("Content-Type", "application/octet-stream")
w.Write([]byte("\r\n"))

chunk := 0
for {
 data := ds.Read(chunk)
 if len(data) == 0 {
  break
 }

 w.Write([]byte(fmt.Sprintf("%x\r\n", len(data))))
 w.Write(data)
 w.Write([]byte("\r\n"))

 chunk++
}
}

func (s *DashServer) handlePost(w http.ResponseWriter, r *http.Request, path string) {
ds := NewDataStream()
s.addStreamToCache(path, ds)

file, err := os.Create(path)
if err != nil {
 http.Error(w, "Failed to create file", http.StatusInternalServerError)
 return
}
defer file.Close()
reader := bufio.NewReader(r.Body)
_, err = io.Copy(file, reader)
if err != nil {
 http.Error(w, "Failed to write file", http.StatusInternalServerError)
 return
}

w.WriteHeader(http.StatusCreated)

// var reader io.Reader
// if r.TransferEncoding[0] == "chunked" {
//  reader = &HTTPChunkedRequestReader{Stream: r.Body}
// } else if r.ContentLength > 0 {
//  reader = &HTTPRequestReader{Stream: r.Body, Remainder: r.ContentLength}
// } else {
//  http.Error(w, "Bad request", http.StatusBadRequest)
//  return
// }

// writePath := filepath.Join(path)
// fmt.Println("$$$$$", writePath)
// outfile, err := os.Create(writePath)
// if err != nil {
//  http.Error(w, "Failed to create file", http.StatusInternalServerError)
//  return
// }
// defer outfile.Close()
// io.Copy(outfile, reader)

// for {
//  data := make([]byte, 1024) // Adjust the buffer size as needed
//  n, err := reader.Read(data)
//  if err != nil && err != io.EOF {
//   http.Error(w, fmt.Sprintf("Failed to read data: %v", err), http.StatusInternalServerError)
//   return
//  }

//  if n == 0 {
//   break
//  }

//  written, err := outfile.Write(data[:n])
//  if err != nil {
//   http.Error(w, fmt.Sprintf("Failed to write data: %v", err), http.StatusInternalServerError)
//   return
//  } else if written < n {
//   http.Error(w, fmt.Sprintf("Partial write: %d < %d", written, n), http.StatusInternalServerError)
//   return
//  }

//  ds.Write(data[:n])
// }

// retCode := http.StatusNoContent
// if _, err := os.Stat(filepath.Join(path)); os.IsNotExist(err) {
//  retCode = http.StatusCreated
// }
// os.Rename(writePath, filepath.Join(path))

// w.WriteHeader(retCode)
// w.Header().Set("Content-Length", "0")
}

func (s *DashServer) logRequest(r *http.Request) {
log.Printf("%s: %s", r.RemoteAddr, r.RequestURI)
}

func (s *DashServer) serveLocalFile(w http.ResponseWriter, path string) {
file, err := os.Open(path)
if err != nil {
http.Error(w, "File not found", http.StatusNotFound)
return
}
defer file.Close()

fileInfo, err := file.Stat()
if err != nil {
 http.Error(w, "Failed to get file info", http.StatusInternalServerError)
 return
}

w.WriteHeader(http.StatusCreated)
w.Header().Set("Content-Length", strconv.FormatInt(fileInfo.Size(), 10))
w.Header().Set("Access-Control-Allow-Origin", "*")
io.Copy(w, file)
}

func (s *DashServer) getStreamFromCache(key string) *DataStream {
ds, ok := s.Streams[key]
if !ok {
return nil
}
return ds
}

func (s *DashServer) addStreamToCache(key string, ds *DataStream) {
s.Streams[key] = ds
}