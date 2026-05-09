# PSoverProxy
Automated Python script Port Scan over Proxy.

## What it does
- Routes scan traffic through an HTTP proxy to reach internal hosts
- Scans a customizable port range with multithreading for speed
- Filters out proxy error pages (Squid, 503, etc.) so only real responses show
- Displays service banners and HTTP responses from open ports
- Shows live scan progress in the terminal

## Usage
```bash
git clone https://github.com/Alisalah-7/PSoverProxy.git
cd PSoverProxy
python3 portscan.py
python3 portscanump.py
```

## Screenshots


## Files
| File | Description |
|------|-------------|
| portscanimp.py | improved version of portscan.py with a feature like filtering based on output |
| portscan.py | basic port scan tool via proxy without no advanced feature |

## Notes
Firstly, execute portscan.py payload and based on outputs add filters manually to Blacklist part inside portscanimp.py, as default I added filters for Squid proxy.
