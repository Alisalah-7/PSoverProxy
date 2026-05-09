#!/usr/bin/env python3
# Proxy Response Enumerator
# Prints every response received through the proxy regardless of content
# Useful for full enumeration without filtering

import requests
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import signal
import sys

counter_lock = Lock()
print_lock = Lock()
scanned = 0
running = True
total_ports = 0

def signal_handler(sig, frame):
    global running
    running = False
    print("\n[!] Scan interrupted.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

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

        # Progress + result printed atomically
        with print_lock:
            print(f"\r[*] Scanning port {port} ({current}/{total_ports})")
            print("=" * 60)
            print(f"[+] Port: {port}")
            print(f"[+] HTTP Status: {r.status_code}")
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
    print(" Proxy Response Enumerator ")
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

    print(f"\n[*] Starting enumeration...")
    print(f"[*] Proxy: {proxy_url}")
    print(f"[*] Target: {target_host}")
    print(f"[*] Range: {start_port}-{end_port}")
    print(f"[*] Threads: {threads}\n")

    with ThreadPoolExecutor(max_workers=threads) as executor:
        for port in ports:
            executor.submit(scan_port, port, proxies, target_host)

    print("\n\n[+] Enumeration completed.")

if __name__ == "__main__":
    main()
