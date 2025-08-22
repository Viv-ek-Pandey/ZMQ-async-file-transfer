package main

import (
	"bufio"
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
	RTT               float64
	CWND              int
	SSThresh          int
	BytesSent         int64
	BytesRetrans      int64
	RetransCount      int
	SendRate          float64
	DeliveryRate      float64
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

type ZmqConnMetaData struct {
	Conn     *zmq.Socket
	ClientId string
	WorkerId string
}

// CSVLogger holds the CSV writer and file handle
type CSVLogger struct {
	writer *csv.Writer
	file   *os.File
}

// InitializeCSVLogger creates a new CSV file and returns a logger
func InitializeCSVLogger(cID string, wID string) (*CSVLogger, error) {
	// Create log directory if it doesn't exist
	timestamp := time.Now().Format("15-04-05")
	logDir := fmt.Sprintf("log/%v", timestamp)
	if err := os.MkdirAll(logDir, 0755); err != nil {
		return nil, fmt.Errorf("failed to create log directory: %v", err)
	}

	// Create filename with current timestamp
	filename := fmt.Sprintf("%s-%s.csv", cID, wID)
	filepath := filepath.Join(logDir, filename)

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
		"state",
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

// LogConnectionData writes connection data to CSV
func (logger *CSVLogger) LogConnectionData(socket ZmqConnMetaData, processConn TCPConnectionInfo, detailedConn *TCPConnectionInfo) error {
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
		if detailedConn.RTT > 0 {
			rtt = fmt.Sprintf("%.3f", detailedConn.RTT)
		}
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

	record := []string{
		timestamp,
		processConn.LocalAddr,
		strconv.Itoa(processConn.LocalPort),
		processConn.RemoteAddr,
		strconv.Itoa(processConn.RemotePort),
		processConn.State,
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
		return fmt.Errorf("failed to write CSV record: %v", err)
	}

	logger.writer.Flush()
	return nil
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
		conn.RTT, _ = strconv.ParseFloat(m[1], 64)
		// variance := m[2] if you want
	}

	conn.CWND = extractInt(`cwnd:(\d+)`)
	conn.SSThresh = extractInt(`ssthresh:(\d+)`)
	conn.BytesSent = extractInt64(`bytes_sent:(\d+)`)
	conn.BytesRetrans = extractInt64(`bytes_retrans:(\d+)`)
	conn.RetransCount = extractInt(`retrans:\d+/(\d+)`)

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

// GetZMQSocketPorts gets connection info by parsing /proc/net/tcp
func GetZMQSocketPorts(targetRemoteAddr string, targetRemotePort int) ([]int, error) {
	file, err := os.Open("/proc/net/tcp")
	if err != nil {
		return nil, fmt.Errorf("failed to open /proc/net/tcp: %v", err)
	}
	defer file.Close()

	var localPorts []int
	scanner := bufio.NewScanner(file)

	// Skip header
	scanner.Scan()

	for scanner.Scan() {
		fields := strings.Fields(scanner.Text())
		if len(fields) < 3 {
			continue
		}

		// Parse remote address (format: ADDR:PORT in hex)
		remoteAddr := fields[2]
		parts := strings.Split(remoteAddr, ":")
		if len(parts) != 2 {
			continue
		}

		// Convert hex port to decimal
		portHex := parts[1]
		port, err := strconv.ParseInt(portHex, 16, 32)
		if err != nil {
			continue
		}

		// Check if this connection is to our target port
		if int(port) == targetRemotePort {
			// Parse local address to get local port
			localAddr := fields[1]
			localParts := strings.Split(localAddr, ":")
			if len(localParts) == 2 {
				localPortHex := localParts[1]
				localPort, err := strconv.ParseInt(localPortHex, 16, 32)
				if err == nil {
					localPorts = append(localPorts, int(localPort))
				}
			}
		}
	}

	return localPorts, scanner.Err()
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

// GetProcessTCPConnections gets TCP connections for current process
func GetProcessTCPConnections(targetPort int) ([]TCPConnectionInfo, error) {
	pid := os.Getpid()

	// Use ss with process filter
	cmd := exec.Command("ss", "-tup", "dst", fmt.Sprintf(":%d", targetPort))
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run ss command: %v", err)
	}

	var connections []TCPConnectionInfo
	lines := strings.Split(string(output), "\n")

	for _, line := range lines {
		if strings.Contains(line, fmt.Sprintf("pid=%d", pid)) {
			conn := parseProcessConnectionLine(line)
			if conn.RemotePort == targetPort {
				connections = append(connections, conn)
			}
		}
	}

	return connections, nil
}

func parseProcessConnectionLine(line string) TCPConnectionInfo {
	// Parse ss -tup output line
	fields := strings.Fields(line)
	if len(fields) < 5 {
		return TCPConnectionInfo{}
	}

	// Extract local and remote addresses
	localAddr := fields[4]
	remoteAddr := fields[5]

	// Parse local address:port
	localParts := strings.Split(localAddr, ":")
	localPort := 0
	if len(localParts) == 2 {
		localPort, _ = strconv.Atoi(localParts[1])
	}

	// Parse remote address:port
	remoteParts := strings.Split(remoteAddr, ":")
	remotePort := 0
	if len(remoteParts) == 2 {
		remotePort, _ = strconv.Atoi(remoteParts[1])
	}

	return TCPConnectionInfo{
		State:      fields[0],
		LocalAddr:  localParts[0],
		LocalPort:  localPort,
		RemoteAddr: remoteParts[0],
		RemotePort: remotePort,
	}
}

// MatchZMQToTCPByProcess matches ZMQ sockets using process-based correlation and logs to CSV
func MatchZMQToTCPByProcess(zmqSockets []ZmqConnMetaData, logger *CSVLogger) error {
	// Get detailed TCP info using ss -ti
	targetPort := 5559
	tcpConnections, err := ParseSSOutput(targetPort)
	if err != nil {
		return fmt.Errorf("failed to get TCP connection details: %v", err)
	}

	// Get process TCP connections using ss -tup
	processConnections, err := GetProcessTCPConnections(targetPort)
	if err != nil {
		return fmt.Errorf("failed to get process connections: %v", err)
	}

	// Correlate ZMQ sockets with TCP connections and log to CSV
	for i, socket := range zmqSockets {
		if i < len(processConnections) {
			processConn := processConnections[i]

			// Find matching detailed connection info
			var detailedConn *TCPConnectionInfo
			for j := range tcpConnections {
				if tcpConnections[j].LocalPort == processConn.LocalPort {
					detailedConn = &tcpConnections[j]
					break
				}
			}

			// Log the connection data to CSV
			if err := logger.LogConnectionData(socket, processConn, detailedConn); err != nil {
				return fmt.Errorf("failed to log connection data: %v", err)
			}
		}
	}

	return nil
}
