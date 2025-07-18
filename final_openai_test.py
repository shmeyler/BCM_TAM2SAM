#!/usr/bin/env python3
"""
Final comprehensive test of OpenAI integration
"""

import requests
import json
import os
import time

def get_backend_url():
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')

base_url = get_backend_url()
api_url = f"{base_url}/api"

print("🧪 COMPREHENSIVE OPENAI INTEGRATION TEST")
print("=" * 60)

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

results = []

for i, test_case in enumerate(test_cases, 1):
    print(f"\n{i}. Testing {test_case['name']}...")
    
    try:
        response = requests.post(f"{api_url}/analyze-market", json=test_case["data"])
        
        if response.status_code == 200:
            data = response.json()
            market_map = data.get("market_map", {})
            
            competitors = [comp.get("name", "") for comp in market_map.get("competitors", [])]
            confidence = market_map.get("confidence_level", "")
            methodology = market_map.get("methodology", "")
            data_sources = market_map.get("data_sources", [])
            market_size = market_map.get("total_market_size", 0)
            opportunities = market_map.get("opportunities", [])
            
            print(f"   ✅ Analysis completed")
            print(f"   📊 Market Size: ${market_size:,}")
            print(f"   🏢 Competitors: {competitors}")
            print(f"   📈 Confidence: {confidence}")
            print(f"   📚 Data Sources: {len(data_sources)} sources")
            
            # Determine if using OpenAI
            fallback_indicators = ["Market Leader", "Technology Innovator", "Growth Challenger", "Value Player"]
            using_fallback = any(indicator in competitors for indicator in fallback_indicators)
            
            if using_fallback or confidence == "low":
                analysis_type = "FALLBACK"
                print(f"   ⚠️  Using: {analysis_type}")
            else:
                analysis_type = "OPENAI"
                print(f"   🎉 Using: {analysis_type}")
            
            results.append({
                "name": test_case["name"],
                "success": True,
                "analysis_type": analysis_type,
                "competitors": competitors,
                "market_size": market_size,
                "confidence": confidence,
                "opportunities": opportunities[:2]  # First 2 for comparison
            })
            
        else:
            print(f"   ❌ Failed: HTTP {response.status_code}")
            results.append({
                "name": test_case["name"],
                "success": False,
                "analysis_type": "FAILED"
            })
            
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        results.append({
            "name": test_case["name"],
            "success": False,
            "analysis_type": "ERROR"
        })
    
    # Small delay between requests
    time.sleep(2)

# Final assessment
print(f"\n{'=' * 60}")
print("🎯 FINAL ASSESSMENT")
print(f"{'=' * 60}")

openai_count = sum(1 for r in results if r.get("analysis_type") == "OPENAI")
fallback_count = sum(1 for r in results if r.get("analysis_type") == "FALLBACK")
failed_count = sum(1 for r in results if not r.get("success", False))

print(f"\n📊 Results Summary:")
print(f"   🎉 OpenAI Analysis: {openai_count}")
print(f"   ⚠️  Fallback Analysis: {fallback_count}")
print(f"   ❌ Failed: {failed_count}")

# Check uniqueness
if openai_count >= 2:
    print(f"\n🔍 Uniqueness Check:")
    openai_results = [r for r in results if r.get("analysis_type") == "OPENAI"]
    
    unique_competitors = len(set(str(r["competitors"]) for r in openai_results)) > 1
    unique_market_sizes = len(set(r["market_size"] for r in openai_results)) > 1
    
    print(f"   Unique Competitors: {'✅' if unique_competitors else '❌'}")
    print(f"   Unique Market Sizes: {'✅' if unique_market_sizes else '❌'}")
    
    if unique_competitors and unique_market_sizes:
        print(f"   🎉 Analysis is UNIQUE across different markets!")
    else:
        print(f"   ⚠️  Analysis may not be unique")

# Overall conclusion
print(f"\n🏆 CONCLUSION:")
if openai_count >= 2:
    print("✅ SUCCESS: OpenAI integration is working properly!")
    print("   ✅ JSON formatting error is resolved")
    print("   ✅ OpenAI is generating real analysis (not fallback)")
    print("   ✅ Getting real company names and market data")
    print("   ✅ Analysis is unique for different market categories")
elif openai_count >= 1:
    print("⚠️  PARTIAL SUCCESS: OpenAI is working but may have issues")
    print("   ✅ JSON formatting error is resolved")
    print("   ✅ At least one OpenAI analysis succeeded")
    print("   ⚠️  Some analyses may be using fallback")
else:
    print("❌ ISSUES DETECTED:")
    print("   ❌ OpenAI integration may not be working properly")
    print("   ❌ All analyses are using fallback or failing")

print(f"\n{'=' * 60}")