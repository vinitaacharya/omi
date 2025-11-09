#!/usr/bin/env python
"""Quick script to verify routes are accessible after server starts"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def check_route(method, path):
    """Check if a route exists by checking the OpenAPI docs"""
    try:
        # Get OpenAPI schema
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code != 200:
            print(f"✗ Could not fetch OpenAPI schema: {response.status_code}")
            return False
        
        schema = response.json()
        paths = schema.get('paths', {})
        
        if path in paths:
            methods_in_path = paths[path].keys()
            if method.lower() in [m.lower() for m in methods_in_path]:
                print(f"✓ {method} {path} - FOUND")
                return True
            else:
                print(f"✗ {method} {path} - Path exists but method {method} not found. Available: {methods_in_path}")
                return False
        else:
            print(f"✗ {method} {path} - NOT FOUND in routes")
            print(f"  Available paths starting with /v2: {[p for p in paths.keys() if p.startswith('/v2')][:10]}")
            return False
    except Exception as e:
        print(f"✗ Error checking {method} {path}: {e}")
        return False

if __name__ == "__main__":
    print("Checking chat router routes...")
    print("=" * 50)
    
    routes_to_check = [
        ("POST", "/v2/messages"),
        ("GET", "/v2/messages"),
        ("POST", "/v2/initial-message"),
    ]
    
    all_found = True
    for method, path in routes_to_check:
        if not check_route(method, path):
            all_found = False
    
    print("=" * 50)
    if all_found:
        print("✓ All routes found!")
        sys.exit(0)
    else:
        print("✗ Some routes are missing!")
        sys.exit(1)

