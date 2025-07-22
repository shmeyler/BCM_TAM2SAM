#!/usr/bin/env python3
"""
Test multiple scenarios to check competitor analysis consistency
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

test_cases = [
    {
        "name": "DTCC",
        "data": {
            "product_name": "DTCC",
            "industry": "Financial Services",
            "geography": "Global", 
            "target_user": "Financial institutions and banks",
            "demand_driver": "Digital transformation in financial markets",
            "transaction_type": "Service fees",
            "key_metrics": "Transaction volume, settlement efficiency",
            "benchmarks": "Post-trade infrastructure market"
        }
    },
    {
        "name": "JPMorgan Chase",
        "data": {
            "product_name": "JPMorgan Chase",
            "industry": "Financial Services",
            "geography": "Global",
            "target_user": "Corporate and retail banking clients",
            "demand_driver": "Digital banking transformation",
            "transaction_type": "Banking fees and interest",
            "key_metrics": "Assets under management, loan volume",
            "benchmarks": "Global banking market"
        }
    }
]

def test_competitor_analysis():
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"{'='*60}")
        
        response = requests.post(f"{api_url}/analyze-market", json=test_case['data'])
        
        if response.status_code != 200:
            print(f"Error: Status code {response.status_code}")
            continue
        
        data = response.json()
        competitors = data['market_map']['competitors']
        competitor_names = [comp['name'] for comp in competitors]
        
        print(f"Product being analyzed: {test_case['name']}")
        print(f"Number of competitors: {len(competitors)}")
        print(f"Competitors: {competitor_names}")
        
        # Check if the product being analyzed appears in competitors
        product_in_competitors = any(test_case['name'].lower() in name.lower() for name in competitor_names)
        print(f"Product appears in competitors: {product_in_competitors}")
        
        # Check for financial services companies
        financial_keywords = ['bank', 'financial', 'chase', 'goldman', 'morgan', 'wells', 'citi', 'dtcc', 'clearstream', 'euroclear']
        financial_competitors = [name for name in competitor_names if any(keyword in name.lower() for keyword in financial_keywords)]
        print(f"Financial services competitors: {financial_competitors}")
        
        print(f"Confidence level: {data['market_map']['confidence_level']}")

if __name__ == "__main__":
    test_competitor_analysis()