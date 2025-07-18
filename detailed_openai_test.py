#!/usr/bin/env python3
"""
Detailed OpenAI Analysis Test
This script tests the specific OpenAI integration issues mentioned in the review request.
"""

import requests
import json
import os
import sys
from typing import Dict, Any, Optional, Tuple

def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

class DetailedOpenAITester:
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def test_openai_integration_detailed(self):
        """Test OpenAI integration with detailed analysis"""
        print(f"\n{'=' * 60}")
        print("DETAILED OPENAI INTEGRATION TEST")
        print(f"{'=' * 60}")
        
        # Test cases from the review request
        test_cases = [
            {
                "name": "Fitness Tracker",
                "data": {
                    "product_name": "Fitness Tracker",
                    "industry": "Wearable Technology", 
                    "geography": "Global",
                    "target_user": "Health-conscious consumers",
                    "demand_driver": "Health and wellness trends",
                    "transaction_type": "One-time Purchase",
                    "key_metrics": "Device sales, user engagement",
                    "benchmarks": "Market growing at 9.2% CAGR"
                }
            },
            {
                "name": "SaaS Software for Small Businesses",
                "data": {
                    "product_name": "Project Management Software",
                    "industry": "Software",
                    "geography": "Global",
                    "target_user": "Small business owners and teams",
                    "demand_driver": "Remote work adoption",
                    "transaction_type": "Subscription",
                    "key_metrics": "Monthly recurring revenue, user adoption",
                    "benchmarks": "SaaS market growing at 18% CAGR"
                }
            },
            {
                "name": "Coffee Shop Chain",
                "data": {
                    "product_name": "Specialty Coffee Chain",
                    "industry": "Food & Beverage",
                    "geography": "United States",
                    "target_user": "Coffee enthusiasts and professionals",
                    "demand_driver": "Premium coffee culture growth",
                    "transaction_type": "Retail Sales",
                    "key_metrics": "Store revenue, customer frequency",
                    "benchmarks": "Specialty coffee market growing at 8% CAGR"
                }
            }
        ]
        
        # First check OpenAI status
        print("\n1. Checking OpenAI Integration Status...")
        response = self.session.get(f"{self.api_url}/test-integrations")
        if response.status_code == 200:
            data = response.json()
            openai_status = data.get("integrations", {}).get("openai", "")
            print(f"   OpenAI Status: {openai_status}")
            
            if openai_status == "OK":
                print("   ✅ OpenAI integration is working")
            else:
                print(f"   ❌ OpenAI integration failed: {openai_status}")
                return False
        else:
            print(f"   ❌ Failed to check integration status: {response.status_code}")
            return False
        
        # Test each market category
        results = []
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. Testing {test_case['name']}...")
            success, analysis_data = self.analyze_market_detailed(test_case)
            results.append((test_case['name'], success, analysis_data))
        
        # Analyze results
        print(f"\n{'=' * 60}")
        print("ANALYSIS RESULTS")
        print(f"{'=' * 60}")
        
        openai_working = True
        unique_analysis = True
        
        for name, success, data in results:
            print(f"\n--- {name} ---")
            if success:
                print(f"✅ Analysis completed successfully")
                
                # Check if using OpenAI vs fallback
                competitors = data.get('competitors', [])
                confidence = data.get('confidence_level', '')
                methodology = data.get('methodology', '')
                market_size = data.get('market_size', 0)
                data_sources = data.get('data_sources', [])
                
                print(f"   Competitors: {competitors}")
                print(f"   Market Size: ${market_size:,}")
                print(f"   Confidence: {confidence}")
                print(f"   Methodology: {methodology}")
                print(f"   Data Sources: {len(data_sources)} sources")
                
                # Determine if using OpenAI or fallback
                fallback_indicators = ["Market Leader", "Technology Innovator", "Growth Challenger", "Value Player"]
                using_fallback = any(indicator in competitors for indicator in fallback_indicators)
                
                if using_fallback:
                    print(f"   ⚠️  Using FALLBACK analysis (generic competitor names)")
                    openai_working = False
                elif confidence == "low" and "fallback" in methodology.lower():
                    print(f"   ⚠️  Using FALLBACK analysis (low confidence + fallback methodology)")
                    openai_working = False
                elif market_size in [1000000000, 5000000000] and not competitors:
                    print(f"   ⚠️  Likely using FALLBACK analysis (default market size + no competitors)")
                    openai_working = False
                else:
                    print(f"   ✅ Using OPENAI analysis")
                
            else:
                print(f"❌ Analysis failed")
                openai_working = False
        
        # Check uniqueness
        if len(results) >= 2:
            print(f"\n--- Uniqueness Check ---")
            analysis1 = results[0][2] if results[0][1] else {}
            analysis2 = results[1][2] if results[1][1] else {}
            
            if analysis1 and analysis2:
                competitors1 = set(analysis1.get('competitors', []))
                competitors2 = set(analysis2.get('competitors', []))
                size1 = analysis1.get('market_size', 0)
                size2 = analysis2.get('market_size', 0)
                
                if competitors1 == competitors2 and size1 == size2:
                    print(f"   ⚠️  Analyses are IDENTICAL (not unique)")
                    unique_analysis = False
                else:
                    print(f"   ✅ Analyses are UNIQUE")
        
        # Final assessment
        print(f"\n{'=' * 60}")
        print("FINAL ASSESSMENT")
        print(f"{'=' * 60}")
        
        if openai_working and unique_analysis:
            print("🎉 SUCCESS: OpenAI integration is working properly!")
            print("   ✅ OpenAI is generating analysis (not using fallback)")
            print("   ✅ Analysis is unique for different market categories")
            print("   ✅ JSON parsing is working correctly")
            return True
        else:
            print("⚠️  ISSUES DETECTED:")
            if not openai_working:
                print("   ❌ OpenAI may not be working properly (using fallback)")
            if not unique_analysis:
                print("   ❌ Analysis may not be unique across different markets")
            return False
    
    def analyze_market_detailed(self, test_case: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Analyze market with detailed response parsing"""
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=test_case["data"]
            )
            
            if response.status_code != 200:
                print(f"   ❌ HTTP Error: {response.status_code}")
                return False, {}
            
            data = response.json()
            
            # Extract key information
            market_map = data.get("market_map", {})
            competitors = [comp.get("name", "") for comp in market_map.get("competitors", [])]
            
            analysis_data = {
                "competitors": competitors,
                "market_size": market_map.get("total_market_size", 0),
                "confidence_level": market_map.get("confidence_level", ""),
                "methodology": market_map.get("methodology", ""),
                "data_sources": market_map.get("data_sources", []),
                "opportunities": market_map.get("opportunities", []),
                "threats": market_map.get("threats", [])
            }
            
            return True, analysis_data
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            return False, {}

if __name__ == "__main__":
    print("Starting Detailed OpenAI Integration Test")
    tester = DetailedOpenAITester()
    success = tester.test_openai_integration_detailed()
    
    if success:
        print("\n✅ All tests passed - OpenAI integration is working correctly!")
        sys.exit(0)
    else:
        print("\n❌ Issues detected - see details above")
        sys.exit(1)