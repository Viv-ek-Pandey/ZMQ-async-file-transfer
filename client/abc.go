package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"regexp"
	"strconv"
	"strings"

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

// ParseSSOutput parses ss -ti output and returns connection info
func ParseSSOutput(targetPort int) ([]TCPConnectionInfo, error) {
	cmd := exec.Command("ss", "-ti", "dst", fmt.Sprintf(":%d", targetPort))
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to run ss command: %v", err)
	}
	// fmt.Println(string(output))

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

	fmt.Println(string(output))

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

// CreateZMQSocket creates and connects a ZMQ DEALER socket
func CreateZMQSocket(endpoint string) (*zmq.Socket, error) {
	socket, err := zmq.NewSocket(zmq.DEALER)
	if err != nil {
		return nil, fmt.Errorf("failed to create ZMQ socket: %v", err)
	}

	// Set socket identity (optional)
	identity := fmt.Sprintf("client-%d", os.Getpid())
	socket.SetIdentity(identity)

	// Connect to endpoint
	err = socket.Connect(endpoint)
	if err != nil {
		socket.Close()
		return nil, fmt.Errorf("failed to connect to %s: %v", endpoint, err)
	}

	return socket, nil
}

type ZmqConnMetaData struct {
	Conn     *zmq.Socket
	ClientId string
	WorkerId string
}

// MatchZMQToTCPByProcess matches ZMQ sockets using process-based correlation
func MatchZMQToTCPByProcess(zmqSockets []ZmqConnMetaData, targetPort int) {
	// fmt.Println("=== ZMQ SOCKET TO TCP CONNECTION MAPPING (Process-based) ===\n")

	// Get detailed TCP info using ss -ti
	tcpConnections, err := ParseSSOutput(targetPort)
	if err != nil {
		fmt.Printf("❌ Failed to get TCP connection details: %v\n", err)
		return
	}

	// Get process TCP connections using ss -tup
	processConnections, err := GetProcessTCPConnections(targetPort)
	if err != nil {
		fmt.Printf("❌ Failed to get process connections: %v\n", err)
		return
	}

	// fmt.Printf("Found %d TCP connections from this process to port %d\n", len(processConnections), targetPort)
	// fmt.Printf("Found %d detailed TCP connection stats\n\n", len(tcpConnections))

	// If we have the same number of ZMQ sockets and TCP connections,
	// we can make reasonable correlations
	// if config.AppConfig.Client.NumberOfWorkers == len(processConnections) {
	fmt.Printf("🔗 Correlating %d ZMQ sockets with %d TCP connections:\n\n",
		len(zmqSockets), len(processConnections))

	for i, socket := range zmqSockets {
		if i < len(processConnections) {
			processConn := processConnections[i]

			fmt.Printf("🔌 ZMQ Socket Client Id #%s Worker ID $%s(Type: %v):\n", socket.ClientId, socket.WorkerId, getSocketTypeString(socket.Conn))
			fmt.Printf("   Process Connection: %s:%d → %s:%d\n",
				processConn.LocalAddr, processConn.LocalPort,
				processConn.RemoteAddr, processConn.RemotePort)

			// Find matching detailed connection info
			var detailedConn *TCPConnectionInfo
			for j := range tcpConnections {
				if tcpConnections[j].LocalPort == processConn.LocalPort {
					detailedConn = &tcpConnections[j]
					break
				}
			}

			if detailedConn != nil {
				printDetailedConnectionInfo(detailedConn)
			} else {
				fmt.Printf("   ⚠️  No detailed stats available for this connection\n")
			}
			fmt.Println()
		}
	}

}

func getSocketTypeString(socket *zmq.Socket) string {
	socketType, err := socket.GetType()
	if err != nil {
		return "UNKNOWN"
	}

	switch socketType {
	case zmq.DEALER:
		return "DEALER"
	case zmq.ROUTER:
		return "ROUTER"
	case zmq.PUSH:
		return "PUSH"
	case zmq.PULL:
		return "PULL"
	case zmq.PUB:
		return "PUB"
	case zmq.SUB:
		return "SUB"
	case zmq.REQ:
		return "REQ"
	case zmq.REP:
		return "REP"
	default:
		return fmt.Sprintf("TYPE_%d", int(socketType))
	}
}

func printDetailedConnectionInfo(conn *TCPConnectionInfo) {
	fmt.Printf("   📊 TCP Stats:\n")
	fmt.Printf("      State: %s\n", conn.State)
	fmt.Printf("      Send Queue: %d bytes (%.2f MB)\n", conn.SendQ, float64(conn.SendQ)/(1024*1024))
	fmt.Printf("      Recv Queue: %d bytes\n", conn.RecvQ)
	if conn.RTT > 0 {
		fmt.Printf("      RTT: %.3f ms\n", conn.RTT)
	}
	if conn.CWND > 0 {
		fmt.Printf("      Congestion Window: %d\n", conn.CWND)
		fmt.Printf("      SS Threshold: %d\n", conn.SSThresh)
	}
	if conn.BytesSent > 0 {
		fmt.Printf("      Bytes Sent: %d (%.2f MB)\n", conn.BytesSent, float64(conn.BytesSent)/(1024*1024))
	}
	// if conn.BytesRetrans > 0 {
	retransPercent := float64(conn.BytesRetrans) / float64(conn.BytesSent) * 100
	fmt.Printf("      Bytes Retransmitted: %d (%.2f MB, %.3f%%)\n",
		conn.BytesRetrans, float64(conn.BytesRetrans)/(1024*1024), retransPercent)
	fmt.Printf("      Retransmission Events: %d\n", conn.RetransCount)
	// }
	if conn.SendRate > 0 {
		fmt.Printf("      Send Rate: %.1f Mbps\n", conn.SendRate)
		fmt.Printf("      Delivery Rate: %.1f Mbps\n", conn.DeliveryRate)
	}

}
