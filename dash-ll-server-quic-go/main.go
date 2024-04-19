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
	"github.com/lucas-clemente/quic-go"
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
	}

	server.Serve()
}

type DashServer struct {
	Address   string
	Port      int
	Directory string
}


func (s *DashServer) Serve() {
	addr := fmt.Sprintf("%s:%d", s.Address, s.Port)
	quicListener, err := quic.ListenAddr(addr, generateTLSConfig(), nil)
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

type DataStream struct {
	Data [][]byte
}

func (ds *DataStream) Read(chunk int) []byte {
	if chunk < len(ds.Data) {
		return ds.Data[chunk]
	}
	return []byte{}
}

func (ds *DataStream) Close() {
	// Implement any cleanup logic here
}

func (s *DashServer) handleGet(w http.ResponseWriter, r *http.Request, path string) {
	localPath := r.URL.Path
	outPath := filepath.Join("./media", localPath)
	fmt.Println("======", outPath)

	// 检查文件是否存在
	_, err := os.Stat(outPath)
	if os.IsNotExist(err) {
		http.Error(w, "File not found", http.StatusNotFound)
		return
	}

	// 读取文件内容并发送给客户端
	file, err := os.Open(outPath)
	if err != nil {
		http.Error(w, "Failed to open file", http.StatusInternalServerError)
		return
	}
	defer file.Close()

	stat, err := file.Stat()
	if err != nil {
		http.Error(w, "Failed to get file info", http.StatusInternalServerError)
		return
	}

	// 设置响应头
	w.Header().Set("Content-Length", fmt.Sprintf("%d", stat.Size()))
	w.Header().Set("Access-Control-Allow-Origin", "*")
	w.WriteHeader(http.StatusOK)

	// 逐块读取并发送文件内容
	buf := make([]byte, 1024)
	for {
		n, err := file.Read(buf)
		if err != nil && err != io.EOF {
			http.Error(w, "Failed to read file", http.StatusInternalServerError)
			return
		}
		if n == 0 {
			break
		}
		if _, err := w.Write(buf[:n]); err != nil {
			log.Println("Failed to write response:", err)
			return
		}
	}
}

func (s *DashServer) handlePost(w http.ResponseWriter, r *http.Request, path string) {
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
}
