#!/usr/bin/env python3
# Internal Proxy Port Scanner
# Scans ports on a target host through an HTTP proxy
# Filters out proxy error pages and only shows interesting responses

import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import signal
import sys

BLACKLIST = [
    "ERR_CONNECT_FAIL",
    "503 Service Unavailable",
    "squid",
    "The requested URL could not be retrieved"
]

counter_lock = Lock()
print_lock = Lock()
scanned = 0
running = True
total_ports = 0

def signal_handler(sig, frame):
    global running
    running = False
    print("\n[!] Scan interrupted by user.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def is_proxy_error(text):
    text = text.lower()
    return any(sig.lower() in text for sig in BLACKLIST)

def scan_port(port, proxies, target_host):
    global scanned, running
    if not running:
        return
    url = f"http://{target_host}:{port}"
    try:
        r = requests.get(
            url,
            proxies=proxies,
            timeout=2
        )
        body = r.text.strip()

        with counter_lock:
            scanned += 1
            current = scanned

        if is_proxy_error(body):
            with print_lock:
                print(
                    f"\r[*] Scanning port {port} ({current}/{total_ports})     ",
                    end="",
                    flush=True
                )
            return

        # Interesting response — progress + result printed atomically so no thread can overwrite between them
        with print_lock:
            print(f"\r[*] Scanning port {port} ({current}/{total_ports})")
            print("=" * 60)
            print(f"[+] Interesting service found on port {port}")
            print(f"[+] Status Code: {r.status_code}")
            print(f"[+] Response Length: {len(body)}")
            print("-" * 60)
            print(body[:400])
            print("=" * 60, flush=True)

    except:
        with counter_lock:
            scanned += 1
            current = scanned
        with print_lock:
            print(
                f"\r[*] Scanning port {port} ({current}/{total_ports})     ",
                end="",
                flush=True
            )

def main():
    global total_ports
    print("=" * 50)
    print(" Internal Proxy Port Scanner ")
    print("=" * 50)
    proxy_host = input("Proxy IP/Host: ").strip()
    proxy_port = input("Proxy Port [3128]: ").strip() or "3128"
    target_host = input("Target Host [127.0.0.1]: ").strip() or "127.0.0.1"
    start_port = int(input("Start Port [1]: ").strip() or "1")
    end_port = int(input("End Port [65535]: ").strip() or "65535")
    threads = int(input("Threads [100]: ").strip() or "100")

    proxy_url = f"http://{proxy_host}:{proxy_port}"
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }

    ports = range(start_port, end_port + 1)
    total_ports = len(ports)

    print(f"\n[*] Starting scan...")
    print(f"[*] Proxy: {proxy_url}")
    print(f"[*] Target: {target_host}")
    print(f"[*] Port Range: {start_port}-{end_port}")
    print(f"[*] Threads: {threads}\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for port in ports:
            executor.submit(scan_port, port, proxies, target_host)

    print("\n\n[+] Scan completed.")

if __name__ == "__main__":
    main()
