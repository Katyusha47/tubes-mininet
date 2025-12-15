#!/bin/bash
# Emergency Fix Script - Run this if pingall fails

echo "========================================"
echo "OpenFlow Simulation - Emergency Fix"
echo "========================================"
echo ""

echo "[1/5] Stopping all Mininet processes..."
sudo mn -c

echo "[2/5] Killing any existing Ryu controllers..."
sudo pkill -f ryu-manager
sleep 2

echo "[3/5] Checking OpenVSwitch status..."
sudo service openvswitch-switch status | head -n 3
if [ $? -ne 0 ]; then
    echo "⚠️  Starting OpenVSwitch..."
    sudo service openvswitch-switch start
    sleep 2
fi

echo "[4/5] Cleaning OVS database..."
sudo ovs-vsctl del-br s1 2>/dev/null
sudo ovs-vsctl del-br s2 2>/dev/null
sudo ovs-vsctl del-br s3 2>/dev/null

echo "[5/5] Ready to start!"
echo ""
echo "========================================"
echo "Now run these commands in order:"
echo "========================================"
echo ""
echo "Terminal 1:"
echo "  ryu-manager controller.py --verbose"
echo ""
echo "Wait 2 seconds, then Terminal 2:"
echo "  sudo python3 topology.py"
echo ""
echo "In Mininet CLI, wait 3-5 seconds, then:"
echo "  mininet> pingall"
echo ""
echo "========================================"
