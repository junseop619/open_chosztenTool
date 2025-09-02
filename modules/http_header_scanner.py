import requests
from .module_template import Module
from colorama import Fore, init

class HttpHeaderScanner(Module):
    def __init__(self):
        super().__init__()
        self.name = "header"
        self.type = "scan"
        self.description = "Checks for important HTTP security headers on a target website."
        # 점검할 주요 보안 헤더 목록과 각 헤더의 부재 시 발생할 수 있는 취약점 정보
        self.security_headers = {
            "Strict-Transport-Security": "Attacker may intercept data via unencrypted HTTP (Man-in-the-Middle).",
            "Content-Security-Policy": "May be vulnerable to Cross-Site Scripting (XSS) and data injection attacks.",
            "X-Content-Type-Options": "Browser may misinterpret file types, leading to XSS attacks (MIME-sniffing).",
            "X-Frame-Options": "May be vulnerable to Clickjacking attacks by being embedded in a malicious iframe.",
            "Referrer-Policy": "Sensitive information in the URL may be leaked to other sites.",
            "Permissions-Policy": "Browser features (camera, mic, etc.) could be used without explicit permission."
        }

    def run(self, target):
        init(autoreset=True)
        url = target
        
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        print(f"[*] [{self.name}] Checking security headers for {url}...")

        try:
            response = requests.get(url, timeout=10, allow_redirects=True)
            headers = response.headers
            
            print(f"[+] [{self.name}] Scan Report for {response.url}:\n")
            
            found_count = 0
            # .keys()를 사용하여 딕셔너리의 키(헤더 이름)를 순회
            for header in self.security_headers.keys():
                if header in headers:
                    print(f"{Fore.GREEN}[+] {header}: Found")
                    found_count += 1
                else:
                    # 헤더가 없을 때, 딕셔너리에서 해당 헤더의 취약점 정보를 가져와 함께 출력
                    vulnerability = self.security_headers[header]
                    print(f"{Fore.RED}[-] {header}: Not Found")
                    print(f" {Fore.RED}└─ Weakness: {vulnerability}")
            
            print(f"\n[*] [{self.name}] Summary: Found {found_count} out of {len(self.security_headers)} recommended security headers.")

        except requests.RequestException as e:
            print(f"[-] [{self.name}] An error occurred: {e}")