#!/bin/bash
# Quick Start Script for OpenFlow Simulation
# This script helps you start the controller and topology correctly

echo "======================================"
echo "OpenFlow Simulation - Quick Start"
echo "======================================"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Please run with sudo: sudo ./quickstart.sh"
    exit 1
fi

# Clean previous Mininet instances
echo "[1/4] Cleaning previous Mininet instances..."
mn -c > /dev/null 2>&1

# Check if Ryu controller is running
echo "[2/4] Checking if Ryu controller is running..."
if pgrep -f "ryu-manager" > /dev/null; then
    echo "✅ Ryu controller is already running"
else
    echo "⚠️  Ryu controller is NOT running!"
    echo ""
    echo "Please start the controller in another terminal first:"
    echo "  ryu-manager controller.py --verbose"
    echo ""
    echo "Press Enter when controller is ready..."
    read
fi

# Start topology
echo "[3/4] Starting Mininet topology..."
echo "Waiting 2 seconds for controller connection..."
sleep 2

echo "[4/4] Launching Mininet CLI..."
echo ""
echo "======================================"
echo "Test Commands:"
echo "======================================"
echo "mininet> pingall              # Test all connectivity"
echo "mininet> h1 ping -c 3 h2      # Should FAIL (ICMP drop)"
echo "mininet> h2 ping -c 3 h3      # Should WORK"
echo "mininet> h3 iperf -s &        # Start iperf server"
echo "mininet> h2 iperf -c 10.0.0.3 # Test TCP"
echo "======================================"
echo ""

python3 topology.py

echo ""
echo "✅ Simulation stopped. Cleaning up..."
mn -c > /dev/null 2>&1
echo "✅ Done!"
