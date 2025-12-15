# Testing Guide - OpenFlow Simulation

## Pre-Test Checklist

### ✅ Step-by-Step Startup

1. **Clean previous sessions**:
   ```bash
   sudo mn -c
   ```

2. **Terminal 1 - Start Controller FIRST**:
   ```bash
   ryu-manager controller.py --verbose
   ```
   
   Wait for this output:
   ```
   loading app controller.py
   instantiating app controller.py of OpenFlowController
   ```

3. **Terminal 2 - Start Topology** (after controller is ready):
   ```bash
   sudo python3 topology.py
   ```
   
   Wait for:
   ```
   *** Starting network
   *** Network configuration:
   ...
   mininet>
   ```

4. **Wait 2-3 seconds** before running tests to ensure all flow rules are installed.

---

## Test Cases

### Test 1: Basic Connectivity Check

```bash
mininet> net
```

Expected output:
```
h1 h1-eth0:s1-eth1
h2 h2-eth0:s1-eth2
h3 h3-eth0:s2-eth1
h4 h4-eth0:s3-eth1
s1 lo:  s1-eth1:h1-eth0 s1-eth2:h2-eth0 s1-eth3:s2-eth2 s1-eth4:s3-eth2
s2 lo:  s2-eth1:h3-eth0 s2-eth2:s1-eth3 s2-eth3:s3-eth3
s3 lo:  s3-eth1:h4-eth0 s3-eth2:s1-eth4 s3-eth3:s2-eth3
c0
```

---

### Test 2: ICMP Drop Rule (h1 cannot ping)

**Test 2.1**: h1 tries to ping h2
```bash
mininet> h1 ping -c 5 h2
```

**Expected Result**: ❌ 100% packet loss
```
5 packets transmitted, 0 received, 100% packet loss
```

**Test 2.2**: h2 tries to ping h1
```bash
mininet> h2 ping -c 5 h1
```

**Expected Result**: ❌ 100% packet loss (h1 cannot respond with ICMP)
```
5 packets transmitted, 0 received, 100% packet loss
```

**Test 2.3**: h1 tries to ping h3
```bash
mininet> h1 ping -c 5 h3
```

**Expected Result**: ❌ 100% packet loss
```
5 packets transmitted, 0 received, 100% packet loss
```

---

### Test 3: Normal Connectivity (Non-h1 hosts)

**Test 3.1**: h2 to h3
```bash
mininet> h2 ping -c 5 h3
```

**Expected Result**: ✅ 0% packet loss
```
5 packets transmitted, 5 received, 0% packet loss
```

**Test 3.2**: h3 to h4
```bash
mininet> h3 ping -c 5 h4
```

**Expected Result**: ✅ 0% packet loss

**Test 3.3**: h2 to h4
```bash
mininet> h2 ping -c 5 h4
```

**Expected Result**: ✅ 0% packet loss

---

### Test 4: Ping All

```bash
mininet> pingall
```

**Expected Result**:
```
*** Ping: testing ping reachability
h1 -> X X X           (h1 cannot ping anyone)
h2 -> X h3 h4         (h2 can ping h3, h4 but not h1)
h3 -> X h2 h4         (h3 can ping h2, h4 but not h1)
h4 -> X h2 h3         (h4 can ping h2, h3 but not h1)
*** Results: 50% dropped (6/12 received)
```

The 50% drop rate is CORRECT because:
- h1 cannot send/receive ICMP (4 failed connections: h1→h2, h1→h3, h1→h4, h2/h3/h4→h1)
- All other hosts can communicate (6 successful: h2↔h3, h2↔h4, h3↔h4)

---

### Test 5: TCP Forwarding (h2 → h3)

**Step 1**: Start iperf server on h3
```bash
mininet> h3 iperf -s -p 5001 &
```

**Step 2**: Connect from h2 to h3
```bash
mininet> h2 iperf -c 10.0.0.3 -p 5001 -t 10
```

**Expected Result**: ✅ TCP connection successful
```
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0-10.0 sec  X.XX GBytes  XXX Mbits/sec
```

**Check Controller Log**: Should show:
```
TCP packet from h2 to h3 on switch X
```

---

### Test 6: MAC Header Modification (h4)

**Step 1**: Open xterm windows
```bash
mininet> xterm h3 h4
```

**Step 2**: In h3 xterm window, start tcpdump:
```bash
tcpdump -i h3-eth0 -nn -v icmp
```

**Step 3**: In h4 xterm window, send ping:
```bash
ping -c 5 10.0.0.3
```

**Expected Result**: 
- Ping should work (✅ 0% packet loss in h4 window)
- In tcpdump output, you should see:
  ```
  XX:XX:XX.XXXXXX 00:00:00:00:00:44 > 00:00:00:00:00:03: ICMP echo request
  ```
  Note: Source MAC is `00:00:00:00:00:44` (modified) instead of `00:00:00:00:00:04` (original h4 MAC)

**Check Controller Log**: Should show:
```
Packet from h4 detected on switch X - modifying headers
```

---

## Troubleshooting During Tests

### Issue: "Network is unreachable"
**Fix**: 
```bash
mininet> exit
sudo mn -c
# Restart controller and topology
```

### Issue: All pings show 100% loss
**Check**:
1. Is controller running? Check Terminal 1
2. Are switches connected? In Mininet: `mininet> net`
3. Try: `mininet> exit`, then `sudo mn -c`, restart both

### Issue: Controller shows too many packet-in messages
**This is normal** during initial learning phase. After 5-10 seconds, it should calm down as flow rules are installed.

### Issue: Cannot see modified MAC in tcpdump
**Check**:
1. Is tcpdump running before you ping?
2. Use correct interface: `h3-eth0`
3. Use `-nn` flag to see MAC addresses
4. Look at SOURCE MAC of incoming packets

---

## Expected Controller Output

When running tests, your controller terminal should show:

```
loading app controller.py
instantiating app controller.py of OpenFlowController
Switch connected: DPID=1
Switch 1: Installed ICMP drop rule for h1
Switch connected: DPID=2
Switch 2: Installed ICMP drop rule for h1
Switch connected: DPID=3
Switch 3: Installed ICMP drop rule for h1

# During h2 to h3 TCP test:
TCP packet from h2 to h3 on switch 1

# During h4 ping test:
Packet from h4 detected on switch 3 - modifying headers
```

---

## Screenshot Checklist for Report

Capture these screenshots:

1. ✅ Controller startup showing "Switch connected" messages
2. ✅ `mininet> net` showing topology
3. ✅ `mininet> h1 ping -c 5 h2` showing 100% packet loss
4. ✅ `mininet> h2 ping -c 5 h3` showing 0% packet loss
5. ✅ `mininet> pingall` showing 50% drop rate
6. ✅ iperf output showing successful TCP transfer
7. ✅ tcpdump showing modified MAC address (00:00:00:00:00:44)
8. ✅ Controller logs showing installed rules

---

## Clean Up After Testing

```bash
# Exit Mininet
mininet> exit

# Clean Mininet
sudo mn -c

# Stop controller (Terminal 1)
Ctrl+C
```

---

## Quick Test Script

Run all basic tests at once:

```bash
mininet> h1 ping -c 3 h2; h2 ping -c 3 h3; h3 ping -c 3 h4; pingall
```

This will quickly show:
- h1 ICMP drop (failed)
- h2-h3 connectivity (success)
- h3-h4 connectivity (success)
- Overall connectivity matrix

---

**Good luck with your testing! 🚀**
