#!/usr/bin/env python3
"""
Final Comprehensive Test for Enhanced Market Map Generator
Tests all scenarios mentioned in the review request
"""

import requests
import json
import os
import time

def get_backend_url():
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

def test_comprehensive_features():
    """Test all features mentioned in the review request"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    print("🚀 COMPREHENSIVE MARKET MAP GENERATOR TESTING")
    print("Testing Enhanced Perspective-Based Analysis and Firmographic Segmentation")
    print("=" * 80)
    
    # Test cases from the review request
    test_cases = [
        {
            "category": "Perspective Analysis - Existing Brand",
            "name": "Apple iPhone Test",
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
            "category": "Perspective Analysis - New Entrant",
            "name": "Generic New Product Test",
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
            "category": "Perspective Analysis - Startup Scenario",
            "name": "Startup Test",
            "data": {
                "product_name": "startup",
                "industry": "Software",
                "geography": "Global",
                "target_user": "Small businesses",
                "demand_driver": "Digital transformation",
                "transaction_type": "SaaS",
                "key_metrics": "MRR, user growth",
                "benchmarks": "SaaS market trends"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": True  # Software industry should trigger B2B
        },
        {
            "category": "Firmographic Segmentation - B2B CRM",
            "name": "CRM Software Test",
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
        },
        {
            "category": "Firmographic Segmentation - B2B SaaS",
            "name": "SaaS Platform Test",
            "data": {
                "product_name": "startup",
                "industry": "SaaS Platform",
                "geography": "United States",
                "target_user": "Enterprise IT departments",
                "demand_driver": "Cloud migration and efficiency",
                "transaction_type": "Annual Subscription",
                "key_metrics": "Platform adoption, integration success",
                "benchmarks": "Enterprise SaaS growth"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": True
        },
        {
            "category": "Firmographic Segmentation - B2B Financial Services",
            "name": "Financial Services Test",
            "data": {
                "product_name": "startup",
                "industry": "Financial Services",
                "geography": "Global",
                "target_user": "Financial institutions and banks",
                "demand_driver": "Digital banking transformation",
                "transaction_type": "Enterprise License",
                "key_metrics": "Transaction volume, compliance metrics",
                "benchmarks": "Fintech market expansion"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": True
        },
        {
            "category": "Firmographic Segmentation - B2C Consumer App",
            "name": "Consumer App Test",
            "data": {
                "product_name": "Consumer App",
                "industry": "Mobile Applications",
                "geography": "Global",
                "target_user": "Mobile users aged 18-35",
                "demand_driver": "Mobile engagement and convenience",
                "transaction_type": "Freemium with in-app purchases",
                "key_metrics": "Daily active users, retention rate",
                "benchmarks": "Mobile app market trends"
            },
            "expected_perspective": "existing_brand",  # "Consumer App" is specific enough
            "should_have_brand_position": True,
            "should_have_firmographics": False  # B2C should not have firmographics
        },
        {
            "category": "Firmographic Segmentation - B2C Retail",
            "name": "Retail Product Test",
            "data": {
                "product_name": "New Product",
                "industry": "Consumer Goods",
                "geography": "United States",
                "target_user": "General consumers",
                "demand_driver": "Consumer spending and trends",
                "transaction_type": "One-time Purchase",
                "key_metrics": "Sales volume, market penetration",
                "benchmarks": "Retail market dynamics"
            },
            "expected_perspective": "new_entrant",
            "should_have_brand_position": False,
            "should_have_firmographics": False  # B2C should not have firmographics
        }
    ]
    
    results = []
    passed_tests = 0
    total_tests = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[{i}/{total_tests}] {test_case['category']}")
        print(f"Testing: {test_case['name']}")
        print(f"Product: {test_case['data']['product_name']}")
        print(f"Industry: {test_case['data']['industry']}")
        print("-" * 60)
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{api_url}/analyze-market",
                json=test_case["data"],
                timeout=180  # 3 minutes timeout for AI calls
            )
            end_time = time.time()
            
            if response.status_code != 200:
                results.append(f"❌ {test_case['name']}: HTTP {response.status_code}")
                print(f"❌ HTTP {response.status_code}: {response.text[:200]}...")
                continue
            
            data = response.json()
            market_map = data.get("market_map", {})
            
            # Test 1: Analysis Perspective
            actual_perspective = market_map.get("analysis_perspective")
            expected_perspective = test_case["expected_perspective"]
            
            if actual_perspective != expected_perspective:
                results.append(f"❌ {test_case['name']}: Wrong perspective - expected {expected_perspective}, got {actual_perspective}")
                print(f"❌ Perspective: Expected {expected_perspective}, got {actual_perspective}")
                continue
            
            print(f"✅ Analysis Perspective: {actual_perspective}")
            
            # Test 2: Brand Position
            brand_position = market_map.get("brand_position")
            should_have_brand_position = test_case["should_have_brand_position"]
            
            if should_have_brand_position and not brand_position:
                results.append(f"❌ {test_case['name']}: Missing brand_position for existing brand")
                print(f"❌ Missing brand_position for existing brand")
                continue
            elif not should_have_brand_position and brand_position:
                results.append(f"❌ {test_case['name']}: Unexpected brand_position for new entrant")
                print(f"❌ Unexpected brand_position: {brand_position[:50]}...")
                continue
            
            if brand_position:
                print(f"✅ Brand Position: {brand_position[:80]}...")
            else:
                print("✅ No Brand Position (as expected for new entrant)")
            
            # Test 3: Firmographic Segmentation
            firmographic_segments = market_map.get("segmentation_by_firmographics", [])
            should_have_firmographics = test_case["should_have_firmographics"]
            
            if should_have_firmographics and not firmographic_segments:
                results.append(f"❌ {test_case['name']}: Missing firmographic segmentation for B2B")
                print(f"❌ Missing firmographic segmentation for B2B industry")
                continue
            elif not should_have_firmographics and firmographic_segments:
                results.append(f"❌ {test_case['name']}: Unexpected firmographic segmentation for B2C")
                print(f"❌ Unexpected firmographic segmentation ({len(firmographic_segments)} segments)")
                continue
            
            if firmographic_segments:
                print(f"✅ Firmographic Segments: {len(firmographic_segments)}")
                for segment in firmographic_segments[:2]:  # Show first 2 segments
                    size_b = segment.get('size_estimate', 0) / 1000000000
                    print(f"   - {segment.get('name', 'Unknown')}: ${size_b:.1f}B ({segment.get('growth_rate', 0)*100:.1f}% growth)")
            else:
                print("✅ No Firmographic Segments (as expected for B2C)")
            
            # Test 4: Data Structure Validation
            required_fields = ["analysis_perspective", "segmentation_by_firmographics"]
            for field in required_fields:
                if field not in market_map:
                    results.append(f"❌ {test_case['name']}: Missing required field {field}")
                    print(f"❌ Missing required field: {field}")
                    continue
            
            # Test 5: Visual Map Validation
            visual_map = data.get("visual_map", {})
            if "firmographic_segments" not in visual_map:
                results.append(f"❌ {test_case['name']}: Missing firmographic_segments in visual_map")
                print(f"❌ Missing firmographic_segments in visual_map")
                continue
            
            visual_firmographic = visual_map.get("firmographic_segments", [])
            if should_have_firmographics and not visual_firmographic:
                print(f"⚠️  Warning: Empty firmographic_segments in visual_map for B2B")
            elif visual_firmographic:
                print(f"✅ Visual Firmographic Segments: {len(visual_firmographic)}")
            
            print(f"✅ Response Time: {end_time - start_time:.1f}s")
            results.append(f"✅ {test_case['name']}: All tests passed")
            passed_tests += 1
            
        except requests.exceptions.Timeout:
            results.append(f"❌ {test_case['name']}: Request timeout (>3 minutes)")
            print("❌ Request timed out")
        except Exception as e:
            results.append(f"❌ {test_case['name']}: {str(e)}")
            print(f"❌ Error: {str(e)}")
    
    # Final Results Summary
    print(f"\n{'=' * 80}")
    print("COMPREHENSIVE TEST RESULTS SUMMARY")
    print(f"{'=' * 80}")
    
    print(f"\n📊 OVERALL RESULTS: {passed_tests}/{total_tests} tests passed")
    
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        print(f"  {result}")
    
    # Feature-specific summary
    perspective_tests = [r for r in results if "Perspective Analysis" in r]
    firmographic_tests = [r for r in results if "Firmographic Segmentation" in r]
    
    perspective_passed = len([r for r in perspective_tests if r.startswith("✅")])
    firmographic_passed = len([r for r in firmographic_tests if r.startswith("✅")])
    
    print(f"\n🎯 FEATURE BREAKDOWN:")
    print(f"  Perspective Analysis: {perspective_passed}/{len(perspective_tests)} passed")
    print(f"  Firmographic Segmentation: {firmographic_passed}/{len(firmographic_tests)} passed")
    
    if passed_tests == total_tests:
        print(f"\n🎉 SUCCESS: All enhanced features working correctly!")
        print("✅ Perspective-based analysis implemented")
        print("✅ Firmographic segmentation for B2B scenarios")
        print("✅ Proper data structure validation")
        print("✅ Visual map integration")
        return True
    else:
        print(f"\n⚠️  PARTIAL SUCCESS: {total_tests - passed_tests} tests failed")
        return False

if __name__ == "__main__":
    success = test_comprehensive_features()
    exit(0 if success else 1)