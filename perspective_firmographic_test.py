#!/usr/bin/env python3
"""
Enhanced Market Map Generator Backend API Test Script
Focus: Testing perspective-based analysis and firmographic segmentation features
"""

import requests
import json
import os
import sys
import time
from typing import Dict, Any, Optional, Tuple

# Get the backend URL from the frontend/.env file
def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

# Test cases for perspective analysis
PERSPECTIVE_TEST_CASES = {
    "existing_brand_apple": {
        "product_name": "Apple iPhone",
        "industry": "Consumer Electronics",
        "geography": "Global",
        "target_user": "Premium smartphone users",
        "demand_driver": "Innovation and brand loyalty",
        "transaction_type": "One-time Purchase",
        "key_metrics": "Unit sales, market share",
        "benchmarks": "Premium smartphone market leader",
        "expected_perspective": "existing_brand",
        "should_have_brand_position": True
    },
    "existing_brand_tesla": {
        "product_name": "Tesla Model S",
        "industry": "Automotive",
        "geography": "North America",
        "target_user": "Luxury EV buyers",
        "demand_driver": "Electric vehicle adoption",
        "transaction_type": "One-time Purchase",
        "key_metrics": "Vehicle sales, charging network",
        "benchmarks": "EV market leader",
        "expected_perspective": "existing_brand",
        "should_have_brand_position": True
    },
    "new_entrant_generic": {
        "product_name": "New Product",
        "industry": "Technology",
        "geography": "United States",
        "target_user": "Tech enthusiasts",
        "demand_driver": "Innovation demand",
        "transaction_type": "Subscription",
        "key_metrics": "User adoption",
        "benchmarks": "Growing market",
        "expected_perspective": "new_entrant",
        "should_have_brand_position": False
    },
    "new_entrant_startup": {
        "product_name": "startup",
        "industry": "Software",
        "geography": "Global",
        "target_user": "Small businesses",
        "demand_driver": "Digital transformation",
        "transaction_type": "SaaS",
        "key_metrics": "MRR, user growth",
        "benchmarks": "SaaS market trends",
        "expected_perspective": "new_entrant",
        "should_have_brand_position": False
    }
}

# Test cases for firmographic segmentation
FIRMOGRAPHIC_TEST_CASES = {
    "b2b_crm_software": {
        "product_name": "CRM Software",
        "industry": "Software",
        "geography": "North America",
        "target_user": "Sales teams and managers",
        "demand_driver": "Sales automation and customer management",
        "transaction_type": "SaaS Subscription",
        "key_metrics": "User adoption, sales pipeline efficiency",
        "benchmarks": "CRM market growing at 12% CAGR",
        "is_b2b": True,
        "should_have_firmographics": True
    },
    "b2b_financial_services": {
        "product_name": "Financial Services Platform",
        "industry": "Financial Services",
        "geography": "Global",
        "target_user": "Financial institutions and banks",
        "demand_driver": "Digital banking transformation",
        "transaction_type": "Enterprise License",
        "key_metrics": "Transaction volume, compliance metrics",
        "benchmarks": "Fintech market expansion",
        "is_b2b": True,
        "should_have_firmographics": True
    },
    "b2b_saas_platform": {
        "product_name": "SaaS Platform",
        "industry": "Business Software",
        "geography": "United States",
        "target_user": "Enterprise IT departments",
        "demand_driver": "Cloud migration and efficiency",
        "transaction_type": "Annual Subscription",
        "key_metrics": "Platform adoption, integration success",
        "benchmarks": "Enterprise SaaS growth",
        "is_b2b": True,
        "should_have_firmographics": True
    },
    "b2c_consumer_app": {
        "product_name": "Consumer App",
        "industry": "Mobile Applications",
        "geography": "Global",
        "target_user": "Mobile users aged 18-35",
        "demand_driver": "Mobile engagement and convenience",
        "transaction_type": "Freemium with in-app purchases",
        "key_metrics": "Daily active users, retention rate",
        "benchmarks": "Mobile app market trends",
        "is_b2b": False,
        "should_have_firmographics": False
    },
    "b2c_retail_product": {
        "product_name": "Retail Product",
        "industry": "Consumer Goods",
        "geography": "United States",
        "target_user": "General consumers",
        "demand_driver": "Consumer spending and trends",
        "transaction_type": "One-time Purchase",
        "key_metrics": "Sales volume, market penetration",
        "benchmarks": "Retail market dynamics",
        "is_b2b": False,
        "should_have_firmographics": False
    }
}

class PerspectiveFirmographicTester:
    """Test class focused on perspective analysis and firmographic segmentation"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def run_all_tests(self) -> bool:
        """Run all perspective and firmographic tests"""
        tests = [
            ("API Health Check", self.test_api_health),
            ("Perspective Analysis Testing", self.test_perspective_analysis),
            ("Firmographic Segmentation Testing", self.test_firmographic_segmentation),
            ("Data Structure Validation", self.test_data_structure_validation)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 70}")
            print(f"Running Test: {test_name}")
            print(f"{'=' * 70}")
            
            try:
                success, message = test_func()
                status = "✅ PASSED" if success else "❌ FAILED"
                results.append((test_name, status, message))
                if not success:
                    all_passed = False
            except Exception as e:
                results.append((test_name, "❌ ERROR", str(e)))
                all_passed = False
                print(f"Error during test: {e}")
        
        # Print summary
        print("\n\n")
        print(f"{'=' * 70}")
        print("PERSPECTIVE & FIRMOGRAPHIC TEST SUMMARY")
        print(f"{'=' * 70}")
        for name, status, message in results:
            print(f"{status} - {name}")
            if status != "✅ PASSED":
                print(f"  └─ {message}")
        
        return all_passed
    
    def test_api_health(self) -> Tuple[bool, str]:
        """Test the API health check endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            if data.get("message") != "Market Map API Ready":
                return False, f"Expected 'Market Map API Ready', got '{data.get('message')}'"
            
            if data.get("version") != "2.0.0":
                return False, f"Expected version '2.0.0', got '{data.get('version')}'"
            
            print(f"✅ API Health Response: {data}")
            return True, "API health check passed"
        except Exception as e:
            return False, f"API health check failed: {str(e)}"
    
    def test_perspective_analysis(self) -> Tuple[bool, str]:
        """Test perspective-based analysis (existing_brand vs new_entrant)"""
        print("🔍 Testing Perspective Analysis...")
        
        results = []
        all_successful = True
        
        for test_name, test_data in PERSPECTIVE_TEST_CASES.items():
            print(f"\n📊 Testing: {test_name}")
            print(f"   Product: {test_data['product_name']}")
            print(f"   Expected Perspective: {test_data['expected_perspective']}")
            
            try:
                # Remove test-specific fields from request
                request_data = {k: v for k, v in test_data.items() 
                              if k not in ['expected_perspective', 'should_have_brand_position']}
                
                response = self.session.post(
                    f"{self.api_url}/analyze-market",
                    json=request_data,
                    timeout=45
                )
                
                if response.status_code != 200:
                    results.append(f"❌ {test_name}: HTTP {response.status_code}")
                    all_successful = False
                    continue
                
                data = response.json()
                market_map = data.get("market_map", {})
                
                # Check analysis_perspective field
                actual_perspective = market_map.get("analysis_perspective")
                expected_perspective = test_data["expected_perspective"]
                
                if actual_perspective != expected_perspective:
                    results.append(f"❌ {test_name}: Expected perspective '{expected_perspective}', got '{actual_perspective}'")
                    all_successful = False
                    continue
                
                # Check brand_position field
                brand_position = market_map.get("brand_position")
                should_have_brand_position = test_data["should_have_brand_position"]
                
                if should_have_brand_position and not brand_position:
                    results.append(f"❌ {test_name}: Expected brand_position for existing brand, but not found")
                    all_successful = False
                    continue
                elif not should_have_brand_position and brand_position:
                    results.append(f"❌ {test_name}: Unexpected brand_position for new entrant: {brand_position}")
                    all_successful = False
                    continue
                
                print(f"   ✅ Perspective: {actual_perspective}")
                if brand_position:
                    print(f"   ✅ Brand Position: {brand_position[:100]}...")
                else:
                    print(f"   ✅ No Brand Position (as expected for new entrant)")
                
                results.append(f"✅ {test_name}: Perspective analysis correct")
                
            except Exception as e:
                results.append(f"❌ {test_name}: {str(e)}")
                all_successful = False
        
        # Print results summary
        print(f"\n📋 PERSPECTIVE ANALYSIS RESULTS:")
        for result in results:
            print(f"  {result}")
        
        if all_successful:
            return True, f"All {len(PERSPECTIVE_TEST_CASES)} perspective tests passed"
        else:
            failed_count = len([r for r in results if r.startswith("❌")])
            return False, f"{failed_count}/{len(PERSPECTIVE_TEST_CASES)} perspective tests failed"
    
    def test_firmographic_segmentation(self) -> Tuple[bool, str]:
        """Test firmographic segmentation for B2B vs B2C scenarios"""
        print("🔍 Testing Firmographic Segmentation...")
        
        results = []
        all_successful = True
        
        for test_name, test_data in FIRMOGRAPHIC_TEST_CASES.items():
            print(f"\n🏢 Testing: {test_name}")
            print(f"   Product: {test_data['product_name']}")
            print(f"   Is B2B: {test_data['is_b2b']}")
            print(f"   Should have firmographics: {test_data['should_have_firmographics']}")
            
            try:
                # Remove test-specific fields from request
                request_data = {k: v for k, v in test_data.items() 
                              if k not in ['is_b2b', 'should_have_firmographics']}
                
                response = self.session.post(
                    f"{self.api_url}/analyze-market",
                    json=request_data,
                    timeout=45
                )
                
                if response.status_code != 200:
                    results.append(f"❌ {test_name}: HTTP {response.status_code}")
                    all_successful = False
                    continue
                
                data = response.json()
                market_map = data.get("market_map", {})
                
                # Check firmographic segmentation
                firmographic_segments = market_map.get("segmentation_by_firmographics", [])
                should_have_firmographics = test_data["should_have_firmographics"]
                
                if should_have_firmographics and not firmographic_segments:
                    results.append(f"❌ {test_name}: Expected firmographic segmentation for B2B, but not found")
                    all_successful = False
                    continue
                elif not should_have_firmographics and firmographic_segments:
                    results.append(f"❌ {test_name}: Unexpected firmographic segmentation for B2C: {len(firmographic_segments)} segments")
                    all_successful = False
                    continue
                
                # If firmographic segments exist, validate their structure
                if firmographic_segments:
                    for i, segment in enumerate(firmographic_segments):
                        required_fields = ["name", "description", "size_estimate", "growth_rate", "key_players"]
                        for field in required_fields:
                            if field not in segment:
                                results.append(f"❌ {test_name}: Missing field '{field}' in firmographic segment {i}")
                                all_successful = False
                                break
                    
                    print(f"   ✅ Firmographic Segments: {len(firmographic_segments)}")
                    for segment in firmographic_segments:
                        print(f"      - {segment.get('name', 'Unknown')}: ${segment.get('size_estimate', 0)/1000000000:.1f}B")
                else:
                    print(f"   ✅ No Firmographic Segments (as expected for B2C)")
                
                # Check visual_map for firmographic_segments
                visual_map = data.get("visual_map", {})
                visual_firmographic = visual_map.get("firmographic_segments", [])
                
                if should_have_firmographics and not visual_firmographic:
                    print(f"   ⚠️  Warning: Missing firmographic_segments in visual_map")
                
                results.append(f"✅ {test_name}: Firmographic segmentation correct")
                
            except Exception as e:
                results.append(f"❌ {test_name}: {str(e)}")
                all_successful = False
        
        # Print results summary
        print(f"\n📋 FIRMOGRAPHIC SEGMENTATION RESULTS:")
        for result in results:
            print(f"  {result}")
        
        if all_successful:
            return True, f"All {len(FIRMOGRAPHIC_TEST_CASES)} firmographic tests passed"
        else:
            failed_count = len([r for r in results if r.startswith("❌")])
            return False, f"{failed_count}/{len(FIRMOGRAPHIC_TEST_CASES)} firmographic tests failed"
    
    def test_data_structure_validation(self) -> Tuple[bool, str]:
        """Test that all new fields are properly included in API responses"""
        print("🔍 Testing Data Structure Validation...")
        
        # Use a B2B existing brand test case to validate all fields
        test_data = {
            "product_name": "Salesforce CRM",
            "industry": "Business Software",
            "geography": "Global",
            "target_user": "Sales teams and managers",
            "demand_driver": "Sales automation and CRM adoption",
            "transaction_type": "SaaS Subscription",
            "key_metrics": "User adoption, sales efficiency",
            "benchmarks": "Leading CRM platform"
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=test_data,
                timeout=45
            )
            
            if response.status_code != 200:
                return False, f"Data structure test failed with HTTP {response.status_code}"
            
            data = response.json()
            
            # Validate top-level structure
            required_top_level = ["market_input", "market_map", "visual_map"]
            for field in required_top_level:
                if field not in data:
                    return False, f"Missing top-level field: {field}"
            
            market_map = data.get("market_map", {})
            
            # Validate new fields in MarketMap
            new_fields = ["analysis_perspective", "segmentation_by_firmographics"]
            for field in new_fields:
                if field not in market_map:
                    return False, f"Missing new field in market_map: {field}"
            
            # Validate analysis_perspective value
            analysis_perspective = market_map.get("analysis_perspective")
            if analysis_perspective not in ["existing_brand", "new_entrant"]:
                return False, f"Invalid analysis_perspective value: {analysis_perspective}"
            
            # For existing brand, validate brand_position
            if analysis_perspective == "existing_brand":
                brand_position = market_map.get("brand_position")
                if not brand_position:
                    return False, "Missing brand_position for existing_brand perspective"
            
            # Validate firmographic segmentation structure
            firmographic_segments = market_map.get("segmentation_by_firmographics", [])
            if firmographic_segments:  # Should have firmographics for B2B
                for segment in firmographic_segments:
                    required_segment_fields = ["name", "description", "size_estimate", "growth_rate", "key_players"]
                    for field in required_segment_fields:
                        if field not in segment:
                            return False, f"Missing field '{field}' in firmographic segment"
            
            # Validate visual_map includes firmographic_segments
            visual_map = data.get("visual_map", {})
            if "firmographic_segments" not in visual_map:
                return False, "Missing firmographic_segments in visual_map"
            
            print("✅ All required fields present:")
            print(f"   - analysis_perspective: {analysis_perspective}")
            if market_map.get("brand_position"):
                print(f"   - brand_position: {market_map.get('brand_position')[:50]}...")
            print(f"   - firmographic segments: {len(firmographic_segments)}")
            print(f"   - visual firmographic segments: {len(visual_map.get('firmographic_segments', []))}")
            
            return True, "Data structure validation passed - all new fields present and properly structured"
            
        except Exception as e:
            return False, f"Data structure validation failed: {str(e)}"


if __name__ == "__main__":
    print("🚀 Starting Enhanced Market Map Generator Perspective & Firmographic Tests")
    print("Focus: Perspective-based analysis and firmographic segmentation features")
    print("=" * 70)
    
    tester = PerspectiveFirmographicTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All perspective and firmographic tests passed successfully!")
        print("✅ Perspective analysis working correctly")
        print("✅ Firmographic segmentation working correctly")
        print("✅ Data structure validation passed")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. See details above.")
        sys.exit(1)