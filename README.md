# OpenFlow Simulation with Mininet
# Tugas Proyek - Simulasi OpenFlow dengan Mininet

## 📋 Deskripsi Proyek

Proyek ini mengimplementasikan simulasi jaringan Software-Defined Networking (SDN) menggunakan Mininet dan OpenFlow controller (Ryu). Simulasi ini mendemonstrasikan konsep Match + Action dalam OpenFlow untuk mengatur traffic jaringan.

### Topologi Jaringan
```
    h1 ──┐
         ├── s1 ── s2 ── h3
    h2 ──┘    │    │
              │    s3 ── h4
              └────┘
```

- **4 Host**: h1 (10.0.0.1), h2 (10.0.0.2), h3 (10.0.0.3), h4 (10.0.0.4)
- **3 Switch**: s1, s2, s3
- **1 Controller**: Ryu (Remote controller di 127.0.0.1:6653)

## 🎯 Fitur OpenFlow Rules

### 1. **Drop ICMP dari h1**
- **Match**: IP protocol = ICMP, Source IP = 10.0.0.1
- **Action**: DROP (tidak ada action)
- **Hasil**: Host h1 tidak dapat melakukan ping ke host lain

### 2. **Forward TCP dari h2 ke h3**
- **Match**: IP protocol = TCP, Source = h2, Destination = h3
- **Action**: Forward melalui path tertentu (s1 → s3 → s2)
- **Hasil**: Traffic TCP diarahkan melalui jalur yang ditentukan

### 3. **Modify Header untuk h4**
- **Match**: Source MAC = 00:00:00:00:00:04 (h4)
- **Action**: Ubah source MAC menjadi 00:00:00:00:00:44
- **Hasil**: Paket dari h4 memiliki MAC address yang dimodifikasi

## 🛠️ Prerequisites

### Untuk Linux/Ubuntu:

#### Option 1: Automatic Installation (Recommended)
```bash
# Run the installation script
chmod +x install.sh
./install.sh
```

#### Option 2: Manual Installation
```bash
# Install Mininet
sudo apt-get update
sudo apt-get install mininet

# Install Python dependencies
pip3 install -r requirements.txt

# Install testing tools
sudo apt-get install iperf tcpdump wireshark
```

### Untuk Windows:
Gunakan salah satu metode berikut:
1. **VirtualBox/VMware** dengan Ubuntu VM
2. **WSL2** (Windows Subsystem for Linux)
3. **Docker** dengan image Mininet

#### WSL2 Setup:
```powershell
# Install WSL2
wsl --install -d Ubuntu

# Masuk ke WSL
wsl

# Install dependencies di WSL
sudo apt-get update
sudo apt-get install mininet python3-pip iperf tcpdump
pip3 install ryu
```

## 🚀 Cara Menjalankan

### ⚠️ IMPORTANT: Start in correct order!

### Step 0: Clean Previous Sessions (CRITICAL)
```bash
# Linux/WSL - Always run this first!
sudo mn -c
```

### Step 1: Start Ryu Controller FIRST
Buka terminal pertama:
```bash
# Linux/WSL
ryu-manager controller.py --verbose
```

Atau di Windows PowerShell (jika menggunakan WSL):
```powershell
wsl ryu-manager controller.py --verbose
```

Output yang diharapkan:
```
loading app controller.py
instantiating app controller.py of OpenFlowController
```

**⚠️ WAIT for "instantiating app" message before proceeding!**

### Step 2: Start Mininet Topology (After controller is ready)
Buka terminal kedua:
```bash
# Linux/WSL
sudo python3 topology.py
```

Atau di Windows PowerShell:
```powershell
wsl sudo python3 topology.py
```

Output yang diharapkan:
```
*** Starting network
*** Waiting for switches to connect to controller
*** Network configuration:
h1: IP=10.0.0.1 MAC=00:00:00:00:00:01
h2: IP=10.0.0.2 MAC=00:00:00:00:00:02
h3: IP=10.0.0.3 MAC=00:00:00:00:00:03
h4: IP=10.0.0.4 MAC=00:00:00:00:00:04
*** Running CLI
mininet>
```

### Step 3: Wait Before Testing (IMPORTANT!)
**⚠️ Wait 3-5 seconds** after Mininet CLI appears before running tests!

This allows:
- Switches to connect to controller
- Flow rules to be installed
- ARP to resolve MAC addresses

## 🧪 Testing

### Test 1: ICMP Drop Rule (h1)
```bash
# Di Mininet CLI
mininet> h1 ping -c 5 h2
```
**Expected Result**: 100% packet loss (ICMP dari h1 di-drop)

```bash
mininet> h2 ping -c 5 h1
```
**Expected Result**: 100% packet loss (h1 tidak bisa menerima/reply)

### Test 2: Normal Connectivity
```bash
mininet> h2 ping -c 5 h3
```
**Expected Result**: 0% packet loss (koneksi normal)

```bash
mininet> pingall
```
**Expected Result**: h1 tidak bisa ping ke siapapun, host lain bisa saling ping

### Test 3: TCP Forwarding (h2 → h3)
```bash
# Start iperf server di h3
mininet> h3 iperf -s &

# Send TCP traffic dari h2 ke h3
mininet> h2 iperf -c 10.0.0.3 -t 10
```
**Expected Result**: TCP connection berhasil, transfer data melalui path yang ditentukan

Monitor di controller terminal untuk melihat log routing.

### Test 4: Header Modification (h4)
```bash
# Open xterm untuk h3 dan h4
mininet> xterm h3 h4
```

Di **h3 xterm**:
```bash
tcpdump -i h3-eth0 -nn -v
```

Di **h4 xterm**:
```bash
ping -c 5 10.0.0.3
```

**Expected Result**: Di output tcpdump, source MAC address akan menjadi `00:00:00:00:00:44` bukan `00:00:00:00:00:04`

### Alternative: Packet Capture dengan Wireshark
```bash
# Di host lain, capture traffic
mininet> h3 tcpdump -i h3-eth0 -w capture.pcap &
mininet> h4 ping -c 10 h3

# Copy file ke host untuk analisis dengan Wireshark
```

## 📊 Output yang Diharapkan

### 1. Controller Output
```
Switch connected: DPID=1
Switch 1: Installed ICMP drop rule for h1
TCP packet from h2 to h3 on switch 1
Packet from h4 detected on switch 3 - modifying headers
```

### 2. Ping Test Results
```
# h1 ping h2 (FAILED)
5 packets transmitted, 0 received, 100% packet loss

# h2 ping h3 (SUCCESS)
5 packets transmitted, 5 received, 0% packet loss

# pingall
h1 -> X X X
h2 -> X h3 h4
h3 -> X h2 h4
h4 -> X h2 h3
```

### 3. Iperf Results
```
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0-10.0 sec  1.10 GBytes   945 Mbits/sec
```

### 4. Tcpdump Output (Header Modification)
```
10.0.0.4 > 10.0.0.3: ICMP echo request
  Source MAC: 00:00:00:00:00:44  <- Modified!
```

## 📁 Struktur File

```
tubes-mininet/
├── topology.py          # Script topologi Mininet
├── controller.py        # Ryu controller dengan OpenFlow rules
├── requirements.txt     # Python dependencies
├── install.sh          # Automatic installation script
├── test_script.sh      # Script testing (reference)
├── README.md           # Dokumentasi ini
└── Tugas Proyek.txt    # Spesifikasi tugas
```

## 🐛 Troubleshooting

### Problem: "command not found: ryu-manager"
**Solution**:
```bash
# Pastikan Ryu terinstall
pip3 install ryu

# Atau gunakan path lengkap
python3 -m ryu.cmd.manager controller.py --verbose
```

### Problem: "Cannot connect to controller"
**Solution**:
1. Pastikan controller sudah running di terminal pertama
2. Check firewall tidak memblokir port 6653
3. Pastikan controller binding ke 127.0.0.1:6653

### Problem: "Permission denied" di Mininet
**Solution**:
```bash
# Gunakan sudo
sudo python topology.py

# Atau tambahkan user ke group
sudo usermod -aG sudo $USER
```

### Problem: WSL tidak bisa menjalankan Mininet
**Solution**:
```powershell
# Pastikan WSL2 (bukan WSL1)
wsl --set-version Ubuntu 2

# Install systemd support
# Edit /etc/wsl.conf
[boot]
systemd=true
```

### Problem: "pingall" shows 100% or high packet loss
**This is the MOST COMMON issue!**

**Solution - Complete Restart**:
```bash
# Step 1: Stop Mininet (in Mininet terminal)
mininet> exit

# Step 2: Clean everything
sudo mn -c

# Step 3: Stop controller (Ctrl+C in controller terminal)

# Step 4: Check if OpenVSwitch is running
sudo service openvswitch-switch status
# If not running: sudo service openvswitch-switch start

# Step 5: Start controller FIRST
ryu-manager controller.py --verbose

# Step 6: WAIT for "instantiating app" message (2-3 seconds)

# Step 7: Start Mininet
sudo python3 topology.py

# Step 8: In Mininet, WAIT 5 seconds before testing
mininet> pingall
```

**Quick fix script**:
```bash
chmod +x fix.sh
./fix.sh
# Then follow the on-screen instructions
```

### Problem: Controller shows infinite "EventOFPPacketIn" messages
**Solution**: This was a bug in the original controller - the updated controller.py fixes this by:
- Properly filtering broadcast/multicast packets
- Installing flow rules correctly to avoid repeated packet-in
- Increasing idle_timeout from 30 to 60 seconds

## 📝 Catatan Untuk Laporan

### Bab III - Implementasi

**Kode Program**:
- `topology.py`: Mendefinisikan topologi dengan Python Mininet API
- `controller.py`: Implementasi Ryu controller dengan 3 match+action rules

**Aturan Match + Action**:
1. **Rule 1**: Match ICMP + Source h1 → Drop
2. **Rule 2**: Match TCP + h2→h3 → Forward via specific path
3. **Rule 3**: Match h4 source → Modify MAC header

### Bab IV - Pengujian

Screenshot yang perlu diambil:
1. Output `pingall` menunjukkan h1 tidak bisa ping
2. Output iperf menunjukkan TCP transfer berhasil
3. Output tcpdump menunjukkan MAC address termodifikasi
4. Controller log menunjukkan rules terpasang

## 🎥 Demo Video Checklist

1. ✅ Tampilkan topologi di Mininet (`net` command)
2. ✅ Tampilkan controller running dengan rules
3. ✅ Demo test ICMP drop (h1 ping fail)
4. ✅ Demo test connectivity normal (h2 ping h3 success)
5. ✅ Demo test iperf TCP
6. ✅ Demo test tcpdump header modification
7. ✅ Tampilkan controller logs

## 📚 Referensi

- [Mininet Documentation](http://mininet.org/)
- [Ryu SDN Framework](https://ryu-sdn.org/)
- [OpenFlow Specification](https://opennetworking.org/software-defined-standards/specifications/)

## 👨‍💻 Author

Project untuk Tugas Proyek - Simulasi OpenFlow dengan Mininet

---
**Good luck with your project! 🚀**
