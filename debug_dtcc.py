#!/usr/bin/env python3
"""
Debug DTCC Analysis - Get full response details
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
    raise ValueError("Backend URL not found in frontend/.env")

DTCC_TEST_DATA = {
    "product_name": "DTCC",
    "industry": "Financial Services",
    "geography": "Global", 
    "target_user": "Financial institutions and banks",
    "demand_driver": "Digital transformation in financial markets",
    "transaction_type": "Service fees",
    "key_metrics": "Transaction volume, settlement efficiency",
    "benchmarks": "Post-trade infrastructure market"
}

def debug_dtcc_analysis():
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    print("Sending DTCC analysis request...")
    response = requests.post(f"{api_url}/analyze-market", json=DTCC_TEST_DATA)
    
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        print(response.text)
        return
    
    data = response.json()
    
    print("\n=== DTCC ANALYSIS RESPONSE ===")
    print(f"Market Input Product: {data['market_input']['product_name']}")
    print(f"Market Input Industry: {data['market_input']['industry']}")
    
    print(f"\nMarket Map TAM: ${data['market_map']['total_market_size']:,.0f}")
    print(f"Growth Rate: {data['market_map']['market_growth_rate']*100:.1f}%")
    
    print(f"\nCompetitors ({len(data['market_map']['competitors'])}):")
    for i, comp in enumerate(data['market_map']['competitors']):
        print(f"  {i+1}. {comp['name']}")
        print(f"     Strengths: {comp['strengths']}")
        print(f"     Weaknesses: {comp['weaknesses']}")
        if 'market_share' in comp:
            print(f"     Market Share: {comp['market_share']}")
        print()
    
    print(f"Data Sources: {data['market_map']['data_sources']}")
    print(f"Confidence Level: {data['market_map']['confidence_level']}")
    
    # Check if this is using OpenAI or fallback
    if data['market_map']['confidence_level'] == 'low':
        print("\n⚠️  WARNING: This appears to be using fallback analysis (low confidence)")
    else:
        print(f"\n✅ Using AI analysis (confidence: {data['market_map']['confidence_level']})")

if __name__ == "__main__":
    debug_dtcc_analysis()