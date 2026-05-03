import subprocess
import time
import requests
import sys
import os

def run_smoke_test():
    print("🚀 Starting Smoke Test...")
    
    # 1. Start server in background
    print("Step 1: Starting Flask server...")
    server_process = subprocess.Popen([sys.executable, "app.py"], 
                                    stdout=subprocess.PIPE, 
                                    stderr=subprocess.PIPE)
    
    time.sleep(3)  # Wait for server to boot
    
    success = True
    try:
        # 2. Check Static Page
        print("Step 2: Checking Home Page...")
        r = requests.get("http://localhost:5000/")
        if r.status_code == 200 and "CIVIX AI" in r.text:
            print("✅ Home Page Loaded.")
        else:
            print("❌ Home Page Failed.")
            success = False

        # 3. Check API structure (without calling real AI if possible, or just checking 500s)
        # We expect a 400 if we send empty data, which confirms the route exists
        print("Step 3: Checking API endpoints...")
        r = requests.post("http://localhost:5000/api/chat", json={})
        if r.status_code == 400:
            print("✅ Chat API Route active.")
        else:
            print(f"⚠️ Chat API returned unexpected code: {r.status_code}")
            
    except Exception as e:
        print(f"❌ Test encountered error: {e}")
        success = False
    finally:
        print("Step 4: Shutting down server...")
        server_process.terminate()
        
    if success:
        print("\n✨ SMOKE TEST PASSED ✨")
        sys.exit(0)
    else:
        print("\n🛑 SMOKE TEST FAILED 🛑")
        sys.exit(1)

if __name__ == "__main__":
    run_smoke_test()
