#!/bin/bash
# Testing script for OpenFlow simulation
# Tests: ping connectivity, ICMP drop rule, TCP forwarding, and header modification

echo "=================================="
echo "OpenFlow Simulation Testing Script"
echo "=================================="
echo ""

# Test 1: Ping from h1 (should be blocked for ICMP)
echo "Test 1: Testing ICMP drop rule (h1 -> h2)"
echo "Expected: Ping should fail due to ICMP drop rule"
echo "Command: h1 ping -c 3 10.0.0.2"
echo "---"
# This will be run in Mininet CLI
echo ""

# Test 2: Ping from h2 to h3 (should work)
echo "Test 2: Testing normal connectivity (h2 -> h3)"
echo "Expected: Ping should succeed"
echo "Command: h2 ping -c 3 10.0.0.3"
echo "---"
echo ""

# Test 3: TCP test with iperf
echo "Test 3: Testing TCP forwarding (h2 -> h3)"
echo "Expected: TCP traffic should flow through specified path"
echo "Commands:"
echo "  On h3: iperf -s -p 5001"
echo "  On h2: iperf -c 10.0.0.3 -p 5001 -t 10"
echo "---"
echo ""

# Test 4: Packet capture for header modification
echo "Test 4: Testing header modification (h4)"
echo "Expected: Packets from h4 should have modified MAC address"
echo "Commands:"
echo "  On h3: tcpdump -i h3-eth0 -nn -v"
echo "  On h4: ping -c 5 10.0.0.3"
echo "  Check if source MAC is modified to 00:00:00:00:00:44"
echo "---"
echo ""

echo "=================================="
echo "Mininet CLI Commands for Testing:"
echo "=================================="
cat << 'EOF'

# Start the network and controller first:
# Terminal 1: Run Ryu controller
ryu-manager controller.py --verbose

# Terminal 2: Run Mininet topology
sudo python topology.py

# In Mininet CLI, run these tests:

# Test 1: ICMP drop from h1
mininet> h1 ping -c 3 h2
# Expected: 100% packet loss

mininet> h2 ping -c 3 h1
# Expected: 100% packet loss (h1 cannot respond)

# Test 2: Normal ping (h2 to h3)
mininet> h2 ping -c 3 h3
# Expected: 0% packet loss

# Test 3: Ping all to see overall connectivity
mininet> pingall

# Test 4: TCP test with iperf
mininet> h3 iperf -s &
mininet> h2 iperf -c 10.0.0.3 -t 10

# Test 5: Header modification check
mininet> h3 tcpdump -i h3-eth0 -n -c 10 &
mininet> h4 ping -c 5 h3
# Check tcpdump output for modified MAC address

# Test 6: Open xterm for detailed testing
mininet> xterm h3 h4
# In h3 xterm: tcpdump -i h3-eth0 -nn -v
# In h4 xterm: ping 10.0.0.3

EOF

echo ""
echo "=================================="
echo "PowerShell Commands (Windows):"
echo "=================================="
cat << 'EOF'

# If running on Windows with WSL or VM:

# Terminal 1: Start Ryu controller
wsl ryu-manager controller.py --verbose

# Terminal 2: Start Mininet (requires Linux/VM)
wsl sudo python topology.py

# Or use SSH to connect to Linux VM/container

EOF
