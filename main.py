import cmd
import shlex
import os
import importlib
import threading
import sys

class MyFramework(cmd.Cmd):
    """나만의 통합 보안 프레임워크"""

#pip install -r requirements.txt

    intro = r"""
    ██████╗ ██╗███╗   ██╗██╗     ██╗██████╗ 
    ██╔══██╗██║████╗  ██║██║     ██║██╔══██╗
    ██████╔╝██║██╔██╗ ██║██║     ██║██████╔╝
    ██╔═══╝ ██║██║╚██╗██║██║     ██║██╔══██╗
    ██║     ██║██║ ╚████║███████╗██║██████╔╝
    ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝╚═════╝ 
    
    Welcome to My Framework! Type 'help' or '?' to list commands.
    """
    prompt = '(my_framework) > '

    def __init__(self):
        super().__init__()
        self.modules = {}
        self.current_module = None
        self.target = None
        self.load_modules()

    def load_modules(self):
        """modules 디렉토리에서 모듈들을 동적으로 로드"""
        # 경로를 resource_path 함수를 통해 찾도록 수정
        module_path = 'modules'
        
        if not os.path.exists(module_path):
            print("[!] 'modules' directory not found!")
            return

        for filename in os.listdir(module_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module_import = importlib.import_module(f"modules.{module_name}")
                    class_name = ''.join(word.capitalize() for word in module_name.split('_'))
                    
                    if hasattr(module_import, class_name):
                        module_class = getattr(module_import, class_name)
                        module_instance = module_class()
                        self.modules[module_instance.name] = module_instance
                        print(f"[*] Loaded module: {module_instance.name}")
                except Exception as e:
                    print(f"[!] Failed to load module {module_name}: {e}")

    # ----- Framework Commands -----

    def do_exit(self, arg):
        """Exits the framework."""
        print('Thank you for using My Framework!')
        return True

    def do_clear(self, arg):
        """Clears the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def do_show(self, arg):
        """Usage: show modules | show options | show target"""
        if arg == 'modules':
            for name, mod in self.modules.items():
                print(f"- {name}: {mod.description}")
        elif arg == 'options':
            if self.current_module:
                print(f"\nModule options for {self.current_module.name}:\n")
                for opt, details in self.current_module.options.items():
                    print(f"  {opt:<15} {str(details['value']):<25} {str(details['required']):<8} {details['description']}")
                print()
            else:
                print("[-] No module selected. Use 'use <module_name>' first.")
        elif arg == 'target':
             if self.target:
                print(f"[*] Current target is: {self.target}")
             else:
                print("[-] No target is set. Use 'set_target <url_or_ip>' to set one.")
        else:
            print("[-] Unknown command. Usage: show modules | show options | show target")
    
    def do_use(self, arg):
        """Select a module to use. Usage: use <module_name>"""
        if arg in self.modules:
            self.current_module = self.modules[arg]
            self.prompt = f'(my_framework: {self.current_module.name}) > '
            print(f"[*] Module selected: {self.current_module.name}")
        else:
            print(f"[-] Unknown module: {arg}")

    def do_set(self, arg):
        """Set an option for the current module. Usage: set <OPTION> <value>"""
        if not self.current_module:
            print("[-] No module selected.")
            return
        
        try:
            parts = shlex.split(arg)
            if len(parts) < 2:
                raise ValueError
            opt_name, opt_value = parts[0], ' '.join(parts[1:])
            
            if opt_name.upper() in self.current_module.options:
                self.current_module.options[opt_name.upper()]['value'] = opt_value
                print(f"[*] {opt_name.upper()} => {opt_value}")
            else:
                print(f"[-] Unknown option: {opt_name}")
        except ValueError:
            print("[-] Usage: set <OPTION> <value>")

    def do_set_target(self, arg):
        """Sets the global target for scanning. Usage: set_target <url_or_ip>"""
        if not arg:
            print("[-] Please provide a target.")
            return
        self.target = arg
        print(f"[*] Global target set to: {self.target}")

    def do_scan(self, arg):
        """
        Runs multiple modules simultaneously against the global target.
        Usage: scan <module1,module2,...>
        """
        if not self.target:
            print("[-] Target not set. Use 'set_target <url_or_ip>' first.")
            return
        if not arg:
            print("[-] Please specify which modules to run. Usage: scan <module1,module2,...>")
            return
        
        module_names = [name.strip() for name in arg.split(',')]
        threads = []

        print(f"\n[*] Starting scan on {self.target} with modules: {', '.join(module_names)}\n")

        for name in module_names:
            if name in self.modules:
                module_instance = self.modules[name]

                # --- 타입 확인 로직 추가 ---
                if module_instance.type != "scan":
                    print(f"[-] Error: Module '{name}' is not a 'scan' type module.")
                    continue # 다음 모듈로 넘어감
                
                thread = threading.Thread(target=module_instance.run, args=(self.target,))
                threads.append(thread)
                thread.start()
            else:
                print(f"[-] Unknown module: {name}")
        
        for thread in threads:
            thread.join()
        
        print("\n[*] All scan modules finished.\n")

    def do_attack(self, arg):
        """
        Runs the specified attack modules.
        Checks if a target is required on a per-module basis.
        """
        if not arg:
            print("[-] Please specify which modules to run. Usage: attack <module1,module2,...>")
            return
    
        module_names = [name.strip() for name in arg.split(',')]
        threads = []

        print(f"\n[*] Starting Attack with modules: {', '.join(module_names)}\n")

        # --- '전체' 타겟 확인 로직을 '모듈별' 확인으로 변경 ---
        for name in module_names:
            if name in self.modules:
                module_instance = self.modules[name]

                # 1. 모듈이 타겟을 필요로 하는지 확인 (기본값은 True로 간주)
                requires_target = getattr(module_instance, 'requires_target', True)
                
                if requires_target and not self.target:
                    print(f"[-] Error: Module '{name}' requires a target. Use 'set_target <url_or_ip>' first.")
                    continue # 타겟이 없으면 이 모듈은 건너뜀

                # 2. 타입 확인 로직은 그대로 유지
                if module_instance.type != "attack":
                    print(f"[-] Error: Module '{name}' is not an 'attack' type module.")
                    continue

                # 3. 타겟 필요 여부에 따라 run() 호출 방식 변경
                if requires_target:
                    thread = threading.Thread(target=module_instance.run, args=(self.target,))
                else:
                    thread = threading.Thread(target=module_instance.run) # target 없이 호출
                
                threads.append(thread)
                thread.start()
            else:
                print(f"[-] Unknown module: {name}")
        
        for thread in threads:
            thread.join()
    
    print("\n[*] All attack modules finished.\n")
    
if __name__ == '__main__':
    try:
        MyFramework().cmdloop()
    except KeyboardInterrupt:
        print("\nExiting.")