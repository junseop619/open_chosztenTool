import whois
from .module_template import Module
from colorama import Fore, init

class WhoisLookup(Module):
    def __init__(self):
        super().__init__()
        self.name = "whois"
        self.type = "scan"
        self.description = "Retrieves WHOIS information for a domain."
        self.options = {} # 이 모듈은 별도 옵션이 필요 없습니다.

    def run(self, target):
        init(autoreset=True)
        domain = target

        print(f"[*] [{self.name}] Retrieving WHOIS information for {domain}...")

        try:
            # whois 라이브러리를 사용하여 도메인 정보 조회
            domain_info = whois.whois(domain)

            # 정보가 없는 경우 처리
            if not domain_info.domain_name:
                print(f"[-] [{self.name}] Could not retrieve WHOIS information for {domain}. The domain may not exist or is private.")
                return

            print(f"[+] [{self.name}] WHOIS Report for {domain}:\n")
            
            # 주요 정보들을 깔끔하게 출력
            key_info = {
                "Domain Name": domain_info.domain_name,
                "Registrar": domain_info.registrar,
                "Creation Date": domain_info.creation_date,
                "Expiration Date": domain_info.expiration_date,
                "Last Updated": domain_info.updated_date,
                "Name Servers": domain_info.name_servers,
                "Emails": domain_info.emails
            }

            for key, value in key_info.items():
                if value:
                    # 값이 리스트인 경우, 쉼표로 구분된 문자열로 변환
                    if isinstance(value, list):
                        value = ', '.join(map(str, value))
                    print(f"  {key:<15}: {value}")

        except Exception as e:
            print(f"[-] [{self.name}] An error occurred: {e}")