#!/usr/bin/env python3
"""
Test script to verify the Invalid format specifier fix
"""

import requests
import json
import os

# Get the backend URL from the frontend/.env file
def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

def test_format_specifier_fix():
    """Test that the Invalid format specifier error has been fixed"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    # Test with a market that will trigger OpenAI error and fallback
    test_market = {
        "product_name": "Test Product with {braces} and format specifiers",
        "industry": "Technology",
        "geography": "Global",
        "target_user": "Test users",
        "demand_driver": "Testing format specifier fix",
        "transaction_type": "Subscription",
        "key_metrics": "Test metrics",
        "benchmarks": "Test benchmarks"
    }
    
    print("🔍 Testing Invalid format specifier fix...")
    print(f"Using API URL: {api_url}")
    
    try:
        response = requests.post(
            f"{api_url}/analyze-market",
            json=test_market,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Request successful - no format specifier error")
            print(f"✅ Product name in response: {data['market_input']['product_name']}")
            print(f"✅ Market size: ${data['market_map']['total_market_size']/1000000000:.1f}B")
            return True
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_format_specifier_fix()
    if success:
        print("\n🎉 Invalid format specifier fix verified!")
    else:
        print("\n⚠️ Fix verification failed")