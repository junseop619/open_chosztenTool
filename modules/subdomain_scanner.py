import requests
import threading
from queue import Queue
from .module_template import Module
from colorama import Fore, init # colorama import 추가

class SubdomainScanner(Module):
    def __init__(self):
        super().__init__()
        self.name = "subdomain"
        self.type = "scan"
        self.description = "Scans for subdomains using a wordlist."
        self.options = {
            'WORDLIST': {'value': 'wordList/subdomains.txt', 'required': True, 'description': 'Path to the wordlist file.'},
            'THREADS': {'value': '20', 'required': False, 'description': 'Number of threads to use.'}
        }
        self.q = Queue()

    def _worker(self, domain):
        while not self.q.empty():
            sub = self.q.get()
            url = f"http://{sub}.{domain}"
            try:
                requests.get(url, timeout=3)
                # print 문을 Fore.GREEN을 사용하도록 수정
                print(f"{Fore.GREEN}[+] [{self.name}] Found: {url}")
            except requests.ConnectionError:
                pass
            finally:
                self.q.task_done()

    def run(self, target):
        # colorama 초기화 (autoreset=True로 설정하면 색상이 자동으로 초기화됨)
        init(autoreset=True)
        
        domain = target
        wordlist_path = self.options['WORDLIST']['value']
        num_threads = int(self.options['THREADS']['value'])

        print(f"[*] [{self.name}] Running subdomain scan on {domain}...")
        try:
            with open(wordlist_path, 'r') as f:
                for line in f:
                    self.q.put(line.strip())
        except FileNotFoundError:
            print(f"[-] [{self.name}] Error: Wordlist file '{wordlist_path}' not found.")
            return

        threads = []
        for _ in range(num_threads):
            t = threading.Thread(target=self._worker, args=(domain,), daemon=True)
            threads.append(t)
            t.start()
        
        self.q.join()
        print(f"[*] [{self.name}] Subdomain scan finished.")