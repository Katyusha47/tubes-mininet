# 🎯 STEP-BY-STEP VISUAL GUIDE

## ⚠️ CRITICAL: You Need TWO Terminal Windows Open At The Same Time!

```
┌─────────────────────────────────┐    ┌─────────────────────────────────┐
│   TERMINAL 1 - CONTROLLER       │    │   TERMINAL 2 - MININET          │
│   (Keep this running!)          │    │   (Start after controller)      │
├─────────────────────────────────┤    ├─────────────────────────────────┤
│                                 │    │                                 │
│ $ ryu-manager controller.py \   │    │  (Wait for controller first!)   │
│     --verbose                   │    │                                 │
│                                 │    │                                 │
│ loading app controller.py       │    │                                 │
│ instantiating app controller... │    │                                 │
│                                 │    │                                 │
│ ← WAIT FOR THIS MESSAGE         │    │                                 │
│                                 │    │                                 │
│ [KEEP RUNNING - DO NOT CLOSE!]  │    │  $ sudo python3 topology.py     │
│                                 │    │                                 │
│ Switch connected: DPID=1        │    │  *** Starting network           │
│ Switch 1: Installed ICMP...     │    │  *** Waiting for switches...    │
│ Switch connected: DPID=2        │    │                                 │
│ Switch 2: Installed ICMP...     │    │  mininet>                       │
│ Switch connected: DPID=3        │    │  mininet> pingall               │
│ Switch 3: Installed ICMP...     │    │                                 │
│                                 │    │  h1 -> X X X                    │
│ [CONTROLLER STAYS RUNNING]      │    │  h2 -> X h3 h4                  │
│                                 │    │  h3 -> X h2 h4                  │
│ ...processing packets...        │    │  h4 -> X h2 h3                  │
│                                 │    │  50% dropped ✓ CORRECT!         │
│                                 │    │                                 │
└─────────────────────────────────┘    └─────────────────────────────────┘
        DO NOT CLOSE THIS!                      Use this one
```

---

## 📋 EXACT STARTUP SEQUENCE

### 🔴 Step 0: Prepare
```bash
# Clean up first
sudo mn -c
```

### 🟢 Step 1: Start Controller (Terminal 1)
```bash
ryu-manager controller.py --verbose
```

**LOOK FOR THIS OUTPUT:**
```
loading app controller.py
instantiating app controller.py of OpenFlowController
```

**✅ SUCCESS** - Controller is now running and waiting for switches

**❌ DO NOT:**
- Close this terminal
- Press Ctrl+C
- Stop the controller
- Start Mininet before you see this message

---

### 🟢 Step 2: Start Mininet (Terminal 2 - KEEP TERMINAL 1 OPEN!)

**Open a NEW terminal window/tab** (don't close terminal 1!)

```bash
sudo python3 topology.py
```

**LOOK FOR THIS OUTPUT IN TERMINAL 1 (Controller):**
```
Switch connected: DPID=1
Switch 1: Installed ICMP drop rule for h1
Switch connected: DPID=2
Switch 2: Installed ICMP drop rule for h1
Switch connected: DPID=3
Switch 3: Installed ICMP drop rule for h1
```

**✅ SUCCESS** - Switches connected to controller!

---

### 🟢 Step 3: Test in Mininet (Terminal 2)

Wait 5 seconds after seeing `mininet>` prompt, then:

```bash
mininet> pingall
```

**EXPECTED OUTPUT:**
```
*** Ping: testing ping reachability
h1 -> X X X
h2 -> X h3 h4
h3 -> X h2 h4
h4 -> X h2 h3
*** Results: 50% dropped (6/12 received)
```

**✅ 50% dropped = CORRECT!** Your OpenFlow rules are working!

---

## ❌ COMMON MISTAKES

### Mistake 1: Closing Controller Too Early
```
Terminal 1: ryu-manager controller.py --verbose
            loading app...
            [You press Ctrl+C]  ← WRONG! DON'T DO THIS!
            Keyboard Interrupt received...

Terminal 2: sudo python3 topology.py
            mininet> pingall
            100% dropped  ← FAILS because no controller!
```

**FIX**: Keep Terminal 1 open the entire time!

---

### Mistake 2: Starting Mininet First
```
Terminal 1: sudo python3 topology.py  ← WRONG ORDER!
            (Mininet starts but can't find controller)

Terminal 2: ryu-manager controller.py
            (Too late, Mininet already gave up)
```

**FIX**: Start controller FIRST, wait, then start Mininet!

---

### Mistake 3: Not Waiting for Controller to Load
```
Terminal 1: ryu-manager controller.py --verbose
            loadi... ← You didn't wait for full message!

Terminal 2: sudo python3 topology.py  ← Started too soon!
```

**FIX**: Wait for "instantiating app" message!

---

## 🎬 FOR WINDOWS (WSL) USERS

### Option 1: Two PowerShell Windows

**PowerShell Window 1:**
```powershell
wsl
cd /mnt/e/tubes-mininet
ryu-manager controller.py --verbose
```
**[KEEP THIS WINDOW OPEN!]**

**PowerShell Window 2:**
```powershell
wsl
cd /mnt/e/tubes-mininet
sudo python3 topology.py
```

---

### Option 2: PowerShell Tabs

1. Open PowerShell
2. Press `Ctrl+Shift+T` to open new tab
3. In Tab 1: `wsl ryu-manager controller.py --verbose`
4. In Tab 2: `wsl sudo python3 topology.py`

---

### Option 3: Windows Terminal (Recommended)

1. Open Windows Terminal
2. Click `+` to add new tab
3. Tab 1 (Controller): `wsl ryu-manager controller.py --verbose`
4. Tab 2 (Mininet): `wsl sudo python3 topology.py`

---

## 🔍 HOW TO VERIFY IT'S WORKING

### In Terminal 1 (Controller) - Should Show:
```
✅ loading app controller.py
✅ instantiating app controller.py of OpenFlowController  
✅ Switch connected: DPID=1
✅ Switch 1: Installed ICMP drop rule for h1
✅ Switch connected: DPID=2
✅ Switch 2: Installed ICMP drop rule for h1
✅ Switch connected: DPID=3
✅ Switch 3: Installed ICMP drop rule for h1
```

### In Terminal 2 (Mininet) - Should Show:
```
✅ *** Starting network
✅ *** Waiting for switches to connect to controller
✅ *** Network configuration:
✅ h1: IP=10.0.0.1 MAC=00:00:00:00:00:01
✅ mininet> 
```

### When You Run pingall:
```
✅ h1 -> X X X           (h1 blocked)
✅ h2 -> X h3 h4         (h2 works)
✅ h3 -> X h2 h4         (h3 works)
✅ h4 -> X h2 h3         (h4 works)
✅ 50% dropped
```

---

## 🆘 EMERGENCY: Still Not Working?

### Check 1: Is controller still running?
```bash
# In another terminal:
ps aux | grep ryu-manager
```
Should show a running process.

### Check 2: Can Mininet reach controller?
```bash
# In Mininet:
mininet> sh ovs-vsctl get-controller s1
```
Should show: `tcp:127.0.0.1:6653`

### Check 3: Are flows installed?
```bash
# In Mininet:
mininet> sh ovs-ofctl -O OpenFlow13 dump-flows s1
```
Should show multiple flows with different priorities.

---

## ✅ SUCCESS CHECKLIST

Before running pingall, verify:

- [ ] Terminal 1 shows "instantiating app"
- [ ] Terminal 1 shows "Switch connected" (3 times)
- [ ] Terminal 1 shows "Installed ICMP drop rule" (3 times)
- [ ] Terminal 1 is STILL RUNNING (not closed)
- [ ] Terminal 2 shows "mininet>" prompt
- [ ] You waited 5 seconds after mininet> appeared
- [ ] You did NOT press Ctrl+C on controller

If ALL checked, then run `pingall` and you should get 50% dropped!

---

**Remember: The controller MUST stay running the entire time!** 🚀
