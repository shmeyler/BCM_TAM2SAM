#!/usr/bin/env python3
"""
Quick test to verify the OpenAI fix
"""

import requests
import json
import os

def get_backend_url():
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')

base_url = get_backend_url()
api_url = f"{base_url}/api"

print("Testing OpenAI fix...")

# Test Fitness Tracker
test_data = {
    "product_name": "Fitness Tracker",
    "industry": "Wearable Technology", 
    "geography": "Global",
    "target_user": "Health-conscious consumers",
    "demand_driver": "Health and wellness trends",
    "transaction_type": "One-time Purchase",
    "key_metrics": "Device sales, user engagement",
    "benchmarks": "Market growing at 9.2% CAGR"
}

response = requests.post(f"{api_url}/analyze-market", json=test_data)

if response.status_code == 200:
    data = response.json()
    market_map = data.get("market_map", {})
    
    competitors = [comp.get("name", "") for comp in market_map.get("competitors", [])]
    confidence = market_map.get("confidence_level", "")
    methodology = market_map.get("methodology", "")
    data_sources = market_map.get("data_sources", [])
    market_size = market_map.get("total_market_size", 0)
    
    print(f"✅ Analysis successful!")
    print(f"   Competitors: {competitors}")
    print(f"   Market Size: ${market_size:,}")
    print(f"   Confidence: {confidence}")
    print(f"   Data Sources: {data_sources}")
    print(f"   Methodology: {methodology}")
    
    # Check if using OpenAI or fallback
    fallback_indicators = ["Market Leader", "Technology Innovator", "Growth Challenger", "Value Player"]
    using_fallback = any(indicator in competitors for indicator in fallback_indicators)
    
    if using_fallback:
        print(f"   ⚠️  Still using FALLBACK analysis")
    elif confidence == "low" and "fallback" in methodology.lower():
        print(f"   ⚠️  Still using FALLBACK analysis")
    else:
        print(f"   🎉 Using OPENAI analysis!")
        
else:
    print(f"❌ Request failed: {response.status_code}")
    print(response.text)