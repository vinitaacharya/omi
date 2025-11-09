#!/usr/bin/env python
"""Test script to verify ngrok endpoint is working"""
import requests
import sys

NGROK_URL = "https://isologous-paulene-wondrously.ngrok-free.dev"
LOCAL_URL = "http://127.0.0.1:8000"

def test_endpoint(base_url, endpoint, method="GET"):
    """Test an endpoint"""
    url = f"{base_url}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json={}, timeout=5)
        else:
            print(f"Unsupported method: {method}")
            return False
        
        print(f"{method} {url} -> {response.status_code}")
        if response.status_code == 404:
            print(f"  ✗ 404 Not Found - Endpoint doesn't exist")
            return False
        elif response.status_code in [200, 201]:
            print(f"  ✓ Success")
            return True
        elif response.status_code == 401:
            print(f"  ✓ Endpoint exists (401 = auth required, which is expected)")
            return True
        elif response.status_code == 422:
            print(f"  ✓ Endpoint exists (422 = validation error, which is expected)")
            return True
        else:
            print(f"  ? Status {response.status_code}")
            return response.status_code != 404
    except requests.exceptions.ConnectionError:
        print(f"  ✗ Connection Error - Server not reachable at {base_url}")
        return False
    except requests.exceptions.Timeout:
        print(f"  ✗ Timeout - Server not responding")
        return False
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 70)
    print("Testing Chat Router Endpoints")
    print("=" * 70)
    
    endpoints_to_test = [
        ("/v2/messages?app_id=", "GET"),
        ("/v2/messages", "POST"),
        ("/docs", "GET"),  # FastAPI docs endpoint
    ]
    
    print("\n1. Testing LOCAL server (127.0.0.1:8000):")
    print("-" * 70)
    local_works = True
    for endpoint, method in endpoints_to_test:
        if not test_endpoint(LOCAL_URL, endpoint, method):
            local_works = False
    
    print("\n2. Testing NGROK server (isologous-paulene-wondrously.ngrok-free.dev):")
    print("-" * 70)
    ngrok_works = True
    for endpoint, method in endpoints_to_test:
        if not test_endpoint(NGROK_URL, endpoint, method):
            ngrok_works = False
    
    print("\n" + "=" * 70)
    print("Results:")
    print("=" * 70)
    
    if local_works:
        print("✓ Local server is working correctly")
    else:
        print("✗ Local server has issues - check if server is running on port 8000")
    
    if ngrok_works:
        print("✓ Ngrok tunnel is working correctly")
        print("\n✅ Everything is configured correctly!")
        print("If Flutter app still gets 404, try:")
        print("  1. Restart the Flutter app")
        print("  2. Clear Flutter app cache")
        print("  3. Rebuild the Flutter app")
    else:
        print("✗ Ngrok tunnel has issues")
        print("\n⚠️  Ngrok is not forwarding correctly!")
        print("Solutions:")
        print("  1. Make sure ngrok is running:")
        print("     ngrok http 8000 --domain=isologous-paulene-wondrously.ngrok-free.dev")
        print("  2. Check ngrok web interface: http://127.0.0.1:4040")
        print("  3. Verify ngrok is forwarding to localhost:8000")
        print("  4. Restart ngrok if needed")
    
    sys.exit(0 if (local_works and ngrok_works) else 1)

