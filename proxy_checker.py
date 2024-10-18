import concurrent.futures
import requests
import socket
import socks
import time
import re
from colorama import Fore, init
from collections import Counter

init(autoreset=True)

error_counter = Counter()

def print_title():
    title = """
  ____                         ____ _               _             
 |  _ \ _ __ _____  ___   _   / ___| |__   ___  ___| | _____ _ __ 
 | |_) | '__/ _ \ \/ / | | | | |   | '_ \ / _ \/ __| |/ / _ \ '__|
 |  __/| | | (_) >  <| |_| | | |___| | | |  __/ (__|   <  __/ |   
 |_|   |_|  \___/_/\_\\__, |  \____|_| |_|\___|\___|_|\_\___|_|   
                      |___/                                       
    """
    print(Fore.MAGENTA + title)

def is_valid_proxy(proxy):
    return bool(re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$', proxy))

def check_proxy(proxy, max_retries=3):
    if not is_valid_proxy(proxy):
        return None
    
    ip, port = proxy.split(':')
    port = int(port)

    for proxy_type in ['http', 'socks4', 'socks5']:
        for attempt in range(max_retries):
            try:
                start = time.time()
                if proxy_type == 'http':
                    s = requests.Session()
                    s.proxies = {'http': f'http://{proxy}', 'https': f'http://{proxy}'}
                    r = s.get('http://httpbin.org/ip', timeout=5)
                    if r.status_code == 200:
                        speed = time.time() - start
                        print(Fore.GREEN + f"[+] HTTP proxy {proxy} is working. Speed: {speed:.2f}s")
                        return proxy, 'http', speed
                else:
                    s = socks.socksocket()
                    s.set_proxy(socks.SOCKS5 if proxy_type == 'socks5' else socks.SOCKS4, ip, port)
                    s.settimeout(5)
                    s.connect(('httpbin.org', 80))
                    speed = time.time() - start
                    print(Fore.GREEN + f"[+] {proxy_type.upper()} proxy {proxy} is working. Speed: {speed:.2f}s")
                    return proxy, proxy_type, speed
            except Exception as e:
                error_type = type(e).__name__
                error_counter[error_type] += 1
                if attempt == max_retries - 1:
                    print(Fore.RED + f"[-] Proxy {proxy} is not working: {error_type}")
                else:
                    print(Fore.YELLOW + f"[!] Retrying proxy {proxy} ({attempt + 1}/{max_retries})")

    return None

def load_proxies(proxy_source):
    try:
        if proxy_source.startswith('http'):
            response = requests.get(proxy_source)
            content = response.text
        else:
            with open(proxy_source, 'r') as f:
                content = f.read()
        
        proxies = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', content)
        return list(set(proxies))  # Remove duplicates
    except Exception as e:
        print(Fore.RED + f"Error loading proxies from {proxy_source}: {e}")
        return []

def main():
    print_title()

    sources = input(Fore.CYAN + "Enter proxy sources (comma-separated URLs or file paths): ").split(',')
    sources = [source.strip() for source in sources]

    proxies = []
    for source in sources:
        proxies.extend(load_proxies(source))

    start_time = time.time()
    total_proxies = len(proxies)

    working_proxies = {"http": [], "socks4": [], "socks5": []}

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        future_to_proxy = {executor.submit(check_proxy, proxy): proxy for proxy in proxies if is_valid_proxy(proxy)}
        for future in concurrent.futures.as_completed(future_to_proxy):
            result = future.result()
            if result:
                proxy, proxy_type, speed = result
                working_proxies[proxy_type].append((proxy, speed))

    for proxy_type, proxies in working_proxies.items():
        if proxies:
            proxies.sort(key=lambda x: x[1])  # Sort by speed
            print(Fore.CYAN + f"\nTotal working {proxy_type.upper()} proxies found: {len(proxies)}")
            with open(f"{proxy_type}_working_proxies.txt", "w") as file:
                for proxy, speed in proxies:
                    file.write(f"{proxy} - Speed: {speed:.2f}s\n")
            print(Fore.CYAN + f"Working {proxy_type.upper()} proxies saved to '{proxy_type}_working_proxies.txt'.")

    elapsed_time = time.time() - start_time
    print(Fore.CYAN + f"\nTotal proxies checked: {total_proxies}")
    print(Fore.CYAN + f"Total time taken: {elapsed_time:.2f} seconds")

    print(Fore.YELLOW + "\nError summary:")
    for error_type, count in error_counter.items():
        print(f"{error_type}: {count}")

if __name__ == "__main__":
    main()
