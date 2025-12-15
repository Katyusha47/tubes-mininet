# 🚨 TROUBLESHOOTING - 100% Packet Loss Fix

## If you're seeing 100% packet loss on pingall, follow this EXACT procedure:

### 🔴 STOP EVERYTHING FIRST

1. **In Mininet terminal** (if running):
   ```bash
   mininet> exit
   ```

2. **In Controller terminal** (if running):
   - Press `Ctrl+C` to stop

3. **Clean Mininet**:
   ```bash
   sudo mn -c
   ```

---

### ✅ CHECK: Is OpenVSwitch Running?

```bash
sudo service openvswitch-switch status
```

**If NOT running**:
```bash
sudo service openvswitch-switch start
sudo service openvswitch-switch status
```

Expected output: `active (running)`

---

### ✅ TEST: Simple Controller First

Before running the complex controller, test if Ryu works at all:

**Terminal 1**:
```bash
ryu-manager simple_controller.py --verbose
```

Wait for: `Switch DPID=X connected` messages

**Terminal 2**:
```bash
sudo python3 topology.py
```

**In Mininet**:
```bash
mininet> pingall
```

**Expected**: ALL pings should work (0% loss)

If this works, your Ryu setup is OK. Proceed to main controller.

If this FAILS, your problem is with Mininet/OVS/Ryu installation.

---

### 🎯 RUN: Main Controller (With Rules)

**Terminal 1 - Controller**:
```bash
# Make sure you're in the project directory
cd /path/to/tubes-mininet

# Start controller
ryu-manager controller.py --verbose
```

**✅ WAIT FOR** these messages:
```
loading app controller.py
instantiating app controller.py of OpenFlowController
```

**Do NOT start Mininet yet!** Wait 2-3 seconds.

---

**Terminal 2 - Mininet**:
```bash
# Clean first
sudo mn -c

# Start topology
sudo python3 topology.py
```

**✅ WAIT FOR** these messages:
```
*** Starting network
*** Waiting for switches to connect to controller
*** Network configuration:
...
mininet>
```

---

**In Mininet CLI**:

**⏱️ WAIT 5 SECONDS** before testing!

Count: 1... 2... 3... 4... 5...

Then:
```bash
mininet> pingall
```

---

### ✅ EXPECTED RESULTS

```
*** Ping: testing ping reachability
h1 -> X X X
h2 -> X h3 h4
h3 -> X h2 h4
h4 -> X h2 h3
*** Results: 50% dropped (6/12 received)
```

**This is CORRECT!**
- h1 cannot ping anyone (ICMP drop rule)
- h2, h3, h4 can all ping each other
- 50% drop = 6 out of 12 connections work

---

### ❌ STILL SEEING 100% LOSS?

#### Check Controller Terminal

Should show:
```
Switch connected: DPID=1
Switch 1: Installed ICMP drop rule for h1
Switch connected: DPID=2
Switch 2: Installed ICMP drop rule for h1
Switch connected: DPID=3
Switch 3: Installed ICMP drop rule for h1
```

If you see infinite `EventOFPPacketIn` messages scrolling:
- Controller is not installing flows properly
- **Solution**: Make sure you're using the UPDATED controller.py

#### Check Mininet can see controller

In Mininet:
```bash
mininet> net
```

Should show `c0` (controller).

If missing:
```bash
mininet> exit
sudo ovs-vsctl set-controller s1 tcp:127.0.0.1:6653
sudo ovs-vsctl set-controller s2 tcp:127.0.0.1:6653
sudo ovs-vsctl set-controller s3 tcp:127.0.0.1:6653
```

---

### 🔧 NUCLEAR OPTION: Complete Reset

```bash
# Stop everything
sudo mn -c
sudo pkill -f ryu-manager
sudo service openvswitch-switch restart

# Wait 5 seconds
sleep 5

# Check OVS is running
sudo service openvswitch-switch status

# Start controller
ryu-manager controller.py --verbose

# Wait 3 seconds
sleep 3

# Start Mininet
sudo python3 topology.py

# In Mininet, wait 5 seconds, then test
mininet> pingall
```

---

### 🔍 DEBUGGING COMMANDS

**Check OVS bridges**:
```bash
sudo ovs-vsctl show
```

**Check flows on switch**:
```bash
sudo ovs-ofctl -O OpenFlow13 dump-flows s1
sudo ovs-ofctl -O OpenFlow13 dump-flows s2
sudo ovs-ofctl -O OpenFlow13 dump-flows s3
```

Should show installed flows with priorities (100, 60, 50, 10, 0).

**Check if switches connect to controller**:
```bash
sudo ovs-vsctl get-controller s1
sudo ovs-vsctl get-controller s2
sudo ovs-vsctl get-controller s3
```

Should show: `tcp:127.0.0.1:6653`

---

### 📞 STILL NOT WORKING?

1. Make sure you pulled the latest controller.py
2. Try the simple_controller.py test
3. Check if you're using Python 3: `python3 --version`
4. Check if Ryu is installed: `ryu-manager --version`
5. Check firewall isn't blocking port 6653

---

### ✅ SUCCESS CHECKLIST

- [ ] OpenVSwitch is running
- [ ] Controller starts without errors
- [ ] Controller shows "Switch connected" messages (3 switches)
- [ ] Mininet starts without errors
- [ ] `pingall` shows 50% drop (correct)
- [ ] h1 cannot ping anyone
- [ ] h2/h3/h4 can ping each other

---

**Good luck! 🚀**
