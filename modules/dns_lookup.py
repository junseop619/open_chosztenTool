import dns.resolver
from .module_template import Module

class DnsLookup(Module):
    def __init__(self):
        super().__init__()
        self.name = "dns"
        self.type = "scan"
        self.description = "Performs DNS lookups to find records. (Mini-nslookup)"
        self.options = {
            'TYPE': {'value': 'A', 'required': True, 'description': 'Record type (A, MX, TXT, NS, AAAA, etc.).'}
        }

    def run(self, target):
        domain = target
        record_type = self.options['TYPE']['value'].upper()
        
        print(f"[*] [{self.name}] Querying '{record_type}' records for {domain}...")

        try:
            answers = dns.resolver.resolve(domain, record_type)
            print(f"[+] [{self.name}] Found {len(answers)} record(s):")
            for rdata in answers:
                print(f"  -> {rdata.to_text()}")
        except dns.resolver.NoAnswer:
            print(f"[-] [{self.name}] No '{record_type}' records found for {domain}.")
        except dns.resolver.NXDOMAIN:
            print(f"[-] [{self.name}] The domain '{domain}' does not exist.")
        except dns.exception.DNSException as e:
            print(f"[-] [{self.name}] An error occurred: {e}")