import requests
import time
import subprocess
import sys

def test_backend():
    print("Starting backend for testing...")
    # Start backend in background
    proc = subprocess.Popen([sys.executable, "-m", "uvicorn", "app.main:app", "--port", "8001"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(5) # Wait for startup

    try:
        # Test Health
        print("Testing /health...")
        resp = requests.get("http://localhost:8001/health")
        assert resp.status_code == 200
        print("Health check passed.")

        # Test Clients
        print("Testing /clients...")
        resp = requests.get("http://localhost:8001/clients")
        if resp.status_code == 200:
            clients = resp.json()
            print(f"Fetched {len(clients)} clients.")
            if len(clients) > 0:
                print(f"Sample client: {clients[0]}")
        else:
            print(f"Failed to fetch clients: {resp.text}")

        # Test Analytics (Mocked)
        print("Testing /analytics...")
        # Use a dummy client ID since it's mocked anyway
        params = {
            "client_id": 123,
            "start_date": "20230101",
            "end_date": "20241231"
        }
        resp = requests.get("http://localhost:8001/analytics", params=params)
        if resp.status_code == 200:
            data = resp.json()
            print("Analytics Data:", data)
            assert "total_cases" in data
            assert "modality_distribution" in data
        else:
            print(f"Failed to fetch analytics: {resp.text}")

    except Exception as e:
        print(f"Test failed: {e}")
        if proc.poll() is not None:
            out, err = proc.communicate()
            print("Backend Output:", out.decode())
            print("Backend Error:", err.decode())
    finally:
        print("Stopping backend...")
        proc.terminate()

if __name__ == "__main__":
    test_backend()
