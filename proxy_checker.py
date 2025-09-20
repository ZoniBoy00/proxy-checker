import concurrent.futures
import requests
import socket
import socks
import time
import re
import threading
from colorama import Fore, init
from collections import Counter

init(autoreset=True)

lock = threading.Lock()
error_counter = Counter()

# Config
TEST_URL = "https://ifconfig.me"
TIMEOUT = 10
MAX_RETRIES = 3


def print_title():
    title = """
  ____                         ____ _               _             
 |  _ \\ _ __ _____  ___   _   / ___| |__   ___  ___| | _____ _ __ 
 | |_) | '__/ _ \\/ / | | | | |   | '_ \\ / _ \\/ __| |/ / _ \\ '__|
 |  __/| | | (_) >  <| |_| | | |___| | | |  __/ (__|   <  __/ |   
 |_|   |_|  \\___/_/\\_\\\\__, |  \\____|_| |_|\\___|\\___|_|\\_\\___|_|   
                      |___/                                       
    """
    print(Fore.MAGENTA + title)


def print_safe(msg, color=Fore.WHITE):
    with lock:
        print(color + msg)


def is_valid_proxy(proxy: str) -> bool:
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', proxy))


def check_proxy(proxy: str):
    if not is_valid_proxy(proxy):
        return None

    ip, port = proxy.split(":")
    port = int(port)

    for proto in ["http", "socks4", "socks5"]:
        for attempt in range(MAX_RETRIES):
            try:
                start = time.time()

                if proto == "http":
                    s = requests.Session()
                    s.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
                    r = s.get(TEST_URL, timeout=TIMEOUT)
                    if r.status_code == 200:
                        speed = time.time() - start
                        print_safe(f"[✔] {proto.upper()} {proxy} works! Speed: {speed:.2f}s", Fore.GREEN)
                        return proxy, proto, speed

                else:
                    sock = socks.socksocket()
                    sock.set_proxy(socks.SOCKS5 if proto == "socks5" else socks.SOCKS4, ip, port)
                    sock.settimeout(TIMEOUT)
                    sock.connect(("ifconfig.me", 80))
                    sock.sendall(b"GET / HTTP/1.1\r\nHost: ifconfig.me\r\n\r\n")
                    resp = sock.recv(100)
                    sock.close()
                    if resp:
                        speed = time.time() - start
                        print_safe(f"[✔] {proto.upper()} {proxy} works! Speed: {speed:.2f}s", Fore.GREEN)
                        return proxy, proto, speed

            except Exception as e:
                error_type = type(e).__name__
                error_counter[f"{proto}:{error_type}"] += 1
                if attempt < MAX_RETRIES - 1:
                    print_safe(f"[!] Retrying {proxy} ({proto.upper()} attempt {attempt+1}/{MAX_RETRIES})", Fore.YELLOW)
                    time.sleep(1)
                else:
                    print_safe(f"[-] {proto.upper()} {proxy} failed after {MAX_RETRIES} attempts ({error_type})", Fore.RED)

    return None


def load_proxies(source: str):
    try:
        if source.startswith("http"):
            resp = requests.get(source, timeout=10)
            content = resp.text
        else:
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()

        proxies = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", content)
        return list(set(proxies))
    except Exception as e:
        print_safe(f"[!] Error loading proxies from {source}: {e}", Fore.RED)
        return []


def save_proxies(working_proxies: dict):
    """Save working proxies per protocol and also all working proxies combined"""
    all_proxies_set = set()

    for proto, proxies in working_proxies.items():
        if proxies:
            proxies.sort(key=lambda x: x[1])
            filename = f"{proto}_working_proxies.txt"
            with open(filename, "w", encoding="utf-8") as f:
                for proxy, _ in proxies:
                    f.write(f"{proxy}\n")
                    all_proxies_set.add(proxy)
            print_safe(f"[✔] {len(proxies)} working {proto.upper()} proxies saved to {filename}", Fore.CYAN)

    # Save all working proxies to a combined file
    if all_proxies_set:
        with open("all_working_proxies.txt", "w", encoding="utf-8") as f:
            for proxy in sorted(all_proxies_set):
                f.write(f"{proxy}\n")
        print_safe(f"[✔] {len(all_proxies_set)} total working proxies saved to all_working_proxies.txt", Fore.CYAN)


def main():
    print_title()
    sources = input(Fore.CYAN + "Enter proxy sources (comma-separated URLs or files): ").split(",")
    sources = [s.strip() for s in sources]

    proxies = []
    for src in sources:
        proxies.extend(load_proxies(src))

    total = len(proxies)
    if not total:
        print_safe("No proxies loaded!", Fore.RED)
        return

    start_time = time.time()
    working_proxies = {"http": [], "socks4": [], "socks5": []}

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxies if is_valid_proxy(p)}
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                proxy, proto, speed = result
                working_proxies[proto].append((proxy, speed))

    save_proxies(working_proxies)

    elapsed = time.time() - start_time
    print_safe(f"\nScan complete. Checked {total} proxies in {elapsed:.2f} seconds.", Fore.CYAN)

    if error_counter:
        print_safe("\nError summary:", Fore.YELLOW)
        for err, count in error_counter.items():
            print_safe(f"{err}: {count}", Fore.YELLOW)


if __name__ == "__main__":
    main()
