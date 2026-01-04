
import sys
import os
import asyncio

# Setup path like run.py
root_dir = "c:\\ThatIDE"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

print(f"Path: {sys.path}")

try:
    from core.orchestrator import Orchestrator
    print(" Import Orchestrator: SUCCESS")
    
    async def test_init():
        orch = Orchestrator(enable_monitoring=True)
        print(" Init Orchestrator: SUCCESS")
        data = orch.get_dashboard_data()
        print(f" Dashboard Data Keys: {list(data.keys())}")

    asyncio.run(test_init())
    
except Exception as e:
    print(f" ERROR: {e}")
    import traceback
    traceback.print_exc()
