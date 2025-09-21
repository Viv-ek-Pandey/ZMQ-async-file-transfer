package main

import (
	"encoding/csv"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"time"

	zmq "github.com/pebbe/zmq4"
)

// TCPConnectionInfo holds parsed ss output
type TCPConnectionInfo struct {
	CongestionControl string
	LocalAddr         string
	LocalPort         int
	RemoteAddr        string
	RemotePort        int
	State             string
	SendQ             int
	RecvQ             int
	RTT               string
	CWND              int
	SSThresh          int
	BytesSent         int64
	BytesRetrans      int64
	RetransCount      int
	SendRate          float64
	DeliveryRate      float64
	RcvWndLimited     string
}

// ZMQSocketInfo holds ZMQ socket information
type ZMQSocketInfo struct {
	Socket     *zmq.Socket
	SocketType zmq.Type
	Endpoint   string
	LocalPort  int
	RemoteAddr string
	RemotePort int
}

// type ZmqConnMetaData struct {
// 	Conn     *zmq.Socket
// 	ClientId string
// 	WorkerId string
// }

// CSVLogger holds the CSV writer and file handle
type CSVLogger struct {
	writer *csv.Writer
	file   *os.File
}

// InitializeCSVLogger creates a new CSV file and returns a logger
func InitializeCSVLogger(cID string, wID string) (*CSVLogger, error) {

	// Create filename with current timestamp
	filename := fmt.Sprintf("%s-%s.csv", cID, wID)
	filepath := filepath.Join(RunLogDir, filename)

	// Create the file
	file, err := os.Create(filepath)
	if err != nil {
		return nil, fmt.Errorf("failed to create CSV file: %v", err)
	}

	writer := csv.NewWriter(file)

	// Write CSV header
	header := []string{
		"timestamp",
		"local_addr",
		"local_port",
		"remote_addr",
		"remote_port",
		"send_queue_bytes",
		"send_queue_mb",
		"recv_queue_bytes",
		"rtt_ms",
		"congestion_window",
		"ss_threshold",
		"bytes_sent",
		"bytes_sent_mb",
		"bytes_retrans",
		"bytes_retrans_mb",
		"retrans_percent",
		"retrans_count",
		"send_rate_mbps",
		"delivery_rate_mbps",
	}

	if err := writer.Write(header); err != nil {
		file.Close()
		return nil, fmt.Errorf("failed to write CSV header: %v", err)
	}

	writer.Flush()

	return &CSVLogger{
		writer: writer,
		file:   file,
	}, nil
}

// Close flushes and closes the CSV logger
func (logger *CSVLogger) Close() error {
	if logger.writer != nil {
		logger.writer.Flush()
	}
	if logger.file != nil {
		return logger.file.Close()
	}
	return nil
}

// Kernel level TCP Data  to CSV
func (logger *CSVLogger) LogConnectionData(processConn TCPConnectionInfo, detailedConn *TCPConnectionInfo) (error, string) {
	timestamp := time.Now().Format("15:04:05")

	// Initialize default values
	var (
		sendQueueMB    = float64(processConn.SendQ) / (1024 * 1024)
		rtt            = ""
		cwnd           = ""
		ssThresh       = ""
		bytesSent      = ""
		bytesSentMB    = ""
		bytesRetrans   = ""
		bytesRetransMB = ""
		retransPercent = ""
		retransCount   = ""
		sendRate       = ""
		deliveryRate   = ""
	)

	// Fill in detailed connection info if available
	if detailedConn != nil {
		rtt = detailedConn.RTT

		if detailedConn.CWND > 0 {
			cwnd = strconv.Itoa(detailedConn.CWND)
			ssThresh = strconv.Itoa(detailedConn.SSThresh)
		}
		if detailedConn.BytesSent > 0 {
			bytesSent = strconv.FormatInt(detailedConn.BytesSent, 10)
			bytesSentMB = fmt.Sprintf("%.2f", float64(detailedConn.BytesSent)/(1024*1024))
		}

		bytesRetrans = strconv.FormatInt(detailedConn.BytesRetrans, 10)
		bytesRetransMB = fmt.Sprintf("%.2f", float64(detailedConn.BytesRetrans)/(1024*1024))

		if detailedConn.BytesSent > 0 {
			retransPercent = fmt.Sprintf("%.3f", float64(detailedConn.BytesRetrans)/float64(detailedConn.BytesSent)*100)
		}

		retransCount = strconv.Itoa(detailedConn.RetransCount)

		if detailedConn.SendRate > 0 {
			sendRate = fmt.Sprintf("%.1f", detailedConn.SendRate)
			deliveryRate = fmt.Sprintf("%.1f", detailedConn.DeliveryRate)
		}
	}

	forServerLog := fmt.Sprintf("Rtt : %s, cnwd : %s, ssThresh : %s, sendRate : %sMBps, rwnd_limited: %s", rtt, cwnd, ssThresh, sendRate, detailedConn.RcvWndLimited)

	record := []string{
		timestamp,
		processConn.LocalAddr,
		strconv.Itoa(processConn.LocalPort),
		processConn.RemoteAddr,
		strconv.Itoa(processConn.RemotePort),
		strconv.Itoa(processConn.SendQ),
		fmt.Sprintf("%.2f", sendQueueMB),
		strconv.Itoa(processConn.RecvQ),
		rtt,
		cwnd,
		ssThresh,
		bytesSent,
		bytesSentMB,
		bytesRetrans,
		bytesRetransMB,
		retransPercent,
		retransCount,
		sendRate,
		deliveryRate,
	}

	if err := logger.writer.Write(record); err != nil {
		return fmt.Errorf("failed to write CSV record: %v", err), ""
	}

	logger.writer.Flush()
	return nil, forServerLog
}

// ParseSSOutput parses ss -ti output and returns connection info
func ParseSSOutput(targetPort int) ([]TCPConnectionInfo, error) {
	cmd := exec.Command("ss", "-ti", "dst", fmt.Sprintf(":%d", targetPort))
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run ss command: %v", err)
	}

	var connections []TCPConnectionInfo
	lines := strings.Split(string(output), "\n")

	for i := 0; i < len(lines); i++ {
		line := strings.TrimSpace(lines[i])
		if strings.HasPrefix(line, "ESTAB") {
			conn, err := parseConnectionLine(line)
			if err != nil {
				continue
			}

			// Parse the detail line that follows
			if i+1 < len(lines) {
				detailLine := strings.TrimSpace(lines[i+1])
				parseDetailLine(&conn, detailLine)
			}

			connections = append(connections, conn)
		}
	}

	return connections, nil
}

func parseConnectionLine(line string) (TCPConnectionInfo, error) {
	// ESTAB 0 8192 54.38.208.202:59824 13.201.191.160:5559
	parts := strings.Fields(line)
	if len(parts) < 5 {
		return TCPConnectionInfo{}, fmt.Errorf("invalid connection line format")
	}

	recvQ, _ := strconv.Atoi(parts[1])
	sendQ, _ := strconv.Atoi(parts[2])

	// Parse local address:port
	localParts := strings.Split(parts[3], ":")
	localPort, _ := strconv.Atoi(localParts[1])

	// Parse remote address:port
	remoteParts := strings.Split(parts[4], ":")
	remotePort, _ := strconv.Atoi(remoteParts[1])

	return TCPConnectionInfo{
		State:      parts[0],
		RecvQ:      recvQ,
		SendQ:      sendQ,
		LocalAddr:  localParts[0],
		LocalPort:  localPort,
		RemoteAddr: remoteParts[0],
		RemotePort: remotePort,
	}, nil
}

func parseDetailLine(conn *TCPConnectionInfo, line string) {
	extractInt := func(pattern string) int {
		re := regexp.MustCompile(pattern)
		if m := re.FindStringSubmatch(line); len(m) > 1 {
			v, _ := strconv.Atoi(m[1])
			return v
		}
		return 0
	}

	extractInt64 := func(pattern string) int64 {
		re := regexp.MustCompile(pattern)
		if m := re.FindStringSubmatch(line); len(m) > 1 {
			v, _ := strconv.ParseInt(m[1], 10, 64)
			return v
		}
		return 0
	}

	// RTT (smoothed / variance)
	if m := regexp.MustCompile(`rtt:([\d.]+)/([\d.]+)`).FindStringSubmatch(line); len(m) == 3 {
		conn.RTT = m[0]
		// fmt.Println("parsed RTT", m[0])

		// variance := m[2] if you want
	}

	conn.CWND = extractInt(`cwnd:(\d+)`)
	conn.SSThresh = extractInt(`ssthresh:(\d+)`)
	conn.BytesSent = extractInt64(`bytes_sent:(\d+)`)
	conn.BytesRetrans = extractInt64(`bytes_retrans:(\d+)`)
	conn.RetransCount = extractInt(`retrans:\d+/(\d+)`)
	if m := regexp.MustCompile(`rwnd_limited:(\d+ms\([\d.]+%\))`).FindStringSubmatch(line); len(m) != 0 {
		conn.RcvWndLimited = m[0]
	}

	// Handle Mbps or Gbps
	if m := regexp.MustCompile(`send ([\d.]+)([GM]bps)`).FindStringSubmatch(line); len(m) == 3 {
		val, _ := strconv.ParseFloat(m[1], 64)
		if m[2] == "Gbps" {
			val *= 1000
		}
		conn.SendRate = val
	}
	if m := regexp.MustCompile(`delivery_rate ([\d.]+)([GM]bps)`).FindStringSubmatch(line); len(m) == 3 {
		val, _ := strconv.ParseFloat(m[1], 64)
		if m[2] == "Gbps" {
			val *= 1000
		}
		conn.DeliveryRate = val
	}
}

// Alternative: Use netstat to correlate ZMQ sockets
func GetZMQSocketInfo(socket *zmq.Socket) (*ZMQSocketInfo, error) {
	// Get ZMQ socket options
	socketType, err := socket.GetType()
	if err != nil {
		return nil, fmt.Errorf("failed to get socket type: %v", err)
	}

	// For DEALER sockets, we can't directly get the TCP connection info
	// Instead, we'll use process-based matching
	return &ZMQSocketInfo{
		Socket:     socket,
		SocketType: socketType,
	}, nil
}

// func GetProcessTCPConnection(targetPort int, t string) (TCPConnectionInfo, error) {
// 	pid := os.Getpid()
// 	var connection TCPConnectionInfo

// 	// Use shell to execute ss -tupn | grep :targetPort
// 	cmd := exec.Command("bash", "-c", fmt.Sprintf("ss -tupn | grep :%d", targetPort))
// 	output, err := cmd.Output()
// 	if err != nil {
// 		return connection, fmt.Errorf("failed to run ss command: %v", err)
// 	}

// 	lines := strings.Split(string(output), "\n")

// 	for _, line := range lines {
// 		line = strings.TrimSpace(line)
// 		if line == "" {
// 			continue
// 		}

// 		fmt.Println("checking line!", line)

// 		// Only process lines that belong to our process
// 		if strings.Contains(line, fmt.Sprintf("pid=%d", pid)) {
// 			fmt.Println("parsing connection for line!", line)
// 			conn := parseProcessConnectionLineNew(line)
// 			if conn.RemotePort == targetPort {
// 				connection = conn
// 			}
// 		}
// 	}

// 	return connection, nil
// }

func parseProcessConnectionLineNew(line string) TCPConnectionInfo {
	// Parse ss -tupn output line
	// Format: tcp ESTAB 0 3500327 54.38.208.202:49394 13.201.191.160:5559 users:(("your_process",pid=12345,fd=10))
	fields := strings.Fields(line)
	if len(fields) < 6 {
		return TCPConnectionInfo{}
	}

	// Extract state (field 1)
	state := fields[1]

	// Extract recv queue (field 2)
	recvQ, _ := strconv.Atoi(fields[2])

	// Extract send queue (field 3)
	sendQ, _ := strconv.Atoi(fields[3])

	// Extract local address:port (field 4)
	localAddr := fields[4]
	localParts := strings.Split(localAddr, ":")
	localPort := 0
	localIP := ""
	if len(localParts) == 2 {
		localIP = localParts[0]
		localPort, _ = strconv.Atoi(localParts[1])
	}
	// fmt.Println(localAddr, localPort, localIP)

	// Extract remote address:port (field 5)
	remoteAddr := fields[5]
	remoteParts := strings.Split(remoteAddr, ":")
	remotePort := 0
	remoteIP := ""
	if len(remoteParts) == 2 {
		remoteIP = remoteParts[0]
		remotePort, _ = strconv.Atoi(remoteParts[1])
	}

	return TCPConnectionInfo{
		State:      state,
		RecvQ:      recvQ,
		SendQ:      sendQ,
		LocalAddr:  localIP,
		LocalPort:  localPort,
		RemoteAddr: remoteIP,
		RemotePort: remotePort,
	}
}

// Get kernel level tcp data for this socket
func GetKernelTcpData(logger *CSVLogger, cID string) (error, string) {
	// Get detailed TCP info using ss -ti
	targetPort := 5559
	tcpConnections, err := ParseSSOutput(targetPort)
	if err != nil {
		return fmt.Errorf("failed to get TCP connection details: %v", err), ""
	}

	tmp, _ := clientPortMap.Load(cID)
	processConnection := tmp.(TCPConnectionInfo)

	// Find matching detailed connection info
	var detailedConn *TCPConnectionInfo
	for j := range tcpConnections {
		if tcpConnections[j].LocalPort == processConnection.LocalPort {
			detailedConn = &tcpConnections[j]
			break
		}
	}
	var forServerLog string
	// Log the connection data to CSV
	if err, forServerLog = logger.LogConnectionData(processConnection, detailedConn); err != nil {
		return fmt.Errorf("failed to log connection data: %v", err), ""
	}

	return nil, forServerLog
}
