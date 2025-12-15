#!/bin/bash
# Complete Installation Script for OpenFlow Mininet Simulation
# Run this script on Ubuntu/Debian Linux or WSL2

echo "======================================"
echo "OpenFlow Mininet Setup Installation"
echo "======================================"
echo ""

# Update system
echo "[1/5] Updating system packages..."
sudo apt-get update

# Install Mininet
echo "[2/5] Installing Mininet..."
sudo apt-get install -y mininet

# Install Python3 and pip
echo "[3/5] Installing Python3 and pip..."
sudo apt-get install -y python3 python3-pip

# Install Ryu and dependencies
echo "[4/5] Installing Ryu controller and Python dependencies..."
pip3 install -r requirements.txt

# Install testing tools
echo "[5/5] Installing testing tools (iperf, tcpdump, net-tools)..."
sudo apt-get install -y iperf tcpdump net-tools

echo ""
echo "======================================"
echo "Installation Complete!"
echo "======================================"
echo ""
echo "Verify installation:"
echo "  - Mininet: sudo mn --version"
echo "  - Ryu: ryu-manager --version"
echo "  - Python3: python3 --version"
echo ""
echo "To run the simulation:"
echo "  Terminal 1: ryu-manager controller.py --verbose"
echo "  Terminal 2: sudo python3 topology.py"
echo ""
