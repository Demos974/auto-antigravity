import psutil
import sys

print("=== EXTRACTING FULL TOKEN ===")

for proc in psutil.process_iter(['pid', 'name']):
    try:
        pname = proc.info['name']
        if not pname: continue
        
        if "antigravity" in pname.lower() or "node" in pname.lower():
            try:
                env = proc.environ()
                if env:
                    for k, v in env.items():
                        if "ANTHROPIC_AUTH_TOKEN" in k:
                            print(f"\n[TOKEN FOUND in PID {proc.info['pid']}]")
                            print(f"{v}")
                            
                            # Also get ports
                            try:
                                connections = proc.net_connections()
                                ports = [c.laddr.port for c in connections if c.status == 'LISTEN']
                                print(f"PORTS: {ports}")
                            except:
                                pass
                            
                            # Only need one good one
                            sys.exit(0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass
