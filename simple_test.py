#!/usr/bin/env python3
"""
Simple test script to validate the new perspective and firmographic features
"""

import requests
import json
import os

def get_backend_url():
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

def test_perspective_and_firmographics():
    """Test the key features with simple test cases"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    # Test cases
    test_cases = [
        {
            "name": "Existing Brand (Apple iPhone) - Should have existing_brand perspective and brand_position",
            "data": {
                "product_name": "Apple iPhone",
                "industry": "Consumer Electronics",
                "geography": "Global",
                "target_user": "Premium smartphone users",
                "demand_driver": "Innovation and brand loyalty",
                "transaction_type": "One-time Purchase",
                "key_metrics": "Unit sales, market share",
                "benchmarks": "Premium smartphone market leader"
            },
            "expected_perspective": "existing_brand",
            "should_have_brand_position": True,
            "should_have_firmographics": False
        },
        {
            "name": "New Product - Should have new_entrant perspective, no brand_position",
            "data": {
                "product_name": "New Product",
                "industry": "Technology",
                "geography": "United States",
                "target_user": "Tech enthusiasts",
                "demand_driver": "Innovation demand",
                "transaction_type": "Subscription",
                "key_metrics": "User adoption",
                "benchmarks": "Growing market"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": False
        },
        {
            "name": "B2B CRM Software - Should have firmographic segmentation",
            "data": {
                "product_name": "startup",
                "industry": "Software",
                "geography": "North America",
                "target_user": "Sales teams and managers",
                "demand_driver": "Sales automation and customer management",
                "transaction_type": "SaaS Subscription",
                "key_metrics": "User adoption, sales pipeline efficiency",
                "benchmarks": "CRM market growing at 12% CAGR"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": True
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\n{'='*60}")
        print(f"Testing: {test_case['name']}")
        print(f"{'='*60}")
        
        try:
            response = requests.post(
                f"{api_url}/analyze-market",
                json=test_case["data"],
                timeout=120  # 2 minutes timeout
            )
            
            if response.status_code != 200:
                results.append(f"❌ {test_case['name']}: HTTP {response.status_code}")
                print(f"❌ HTTP {response.status_code}: {response.text}")
                continue
            
            data = response.json()
            market_map = data.get("market_map", {})
            
            # Test perspective analysis
            actual_perspective = market_map.get("analysis_perspective")
            expected_perspective = test_case["expected_perspective"]
            
            if actual_perspective != expected_perspective:
                results.append(f"❌ {test_case['name']}: Wrong perspective - expected {expected_perspective}, got {actual_perspective}")
                continue
            
            print(f"✅ Perspective: {actual_perspective}")
            
            # Test brand position
            brand_position = market_map.get("brand_position")
            should_have_brand_position = test_case["should_have_brand_position"]
            
            if should_have_brand_position and not brand_position:
                results.append(f"❌ {test_case['name']}: Missing brand_position for existing brand")
                continue
            elif not should_have_brand_position and brand_position:
                results.append(f"❌ {test_case['name']}: Unexpected brand_position for new entrant")
                continue
            
            if brand_position:
                print(f"✅ Brand Position: {brand_position[:100]}...")
            else:
                print("✅ No Brand Position (as expected)")
            
            # Test firmographic segmentation
            firmographic_segments = market_map.get("segmentation_by_firmographics", [])
            should_have_firmographics = test_case["should_have_firmographics"]
            
            if should_have_firmographics and not firmographic_segments:
                results.append(f"❌ {test_case['name']}: Missing firmographic segmentation for B2B")
                continue
            elif not should_have_firmographics and firmographic_segments:
                results.append(f"❌ {test_case['name']}: Unexpected firmographic segmentation for B2C")
                continue
            
            if firmographic_segments:
                print(f"✅ Firmographic Segments: {len(firmographic_segments)}")
                for segment in firmographic_segments:
                    print(f"   - {segment.get('name', 'Unknown')}: ${segment.get('size_estimate', 0)/1000000000:.1f}B")
            else:
                print("✅ No Firmographic Segments (as expected)")
            
            results.append(f"✅ {test_case['name']}: All tests passed")
            
        except requests.exceptions.Timeout:
            results.append(f"❌ {test_case['name']}: Request timeout")
            print("❌ Request timed out")
        except Exception as e:
            results.append(f"❌ {test_case['name']}: {str(e)}")
            print(f"❌ Error: {str(e)}")
    
    # Print final results
    print(f"\n{'='*60}")
    print("FINAL TEST RESULTS")
    print(f"{'='*60}")
    
    for result in results:
        print(result)
    
    passed = len([r for r in results if r.startswith("✅")])
    total = len(results)
    
    print(f"\nSUMMARY: {passed}/{total} tests passed")
    
    return passed == total

if __name__ == "__main__":
    success = test_perspective_and_firmographics()
    if success:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️ Some tests failed!")