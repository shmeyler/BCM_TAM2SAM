#!/usr/bin/env python3
"""
Enhanced Market Map Generator Backend API Test Script
This script tests the functionality of the Market Map Generator backend API endpoints,
with specific focus on testing multiple market categories and verifying the OpenAI JSON parsing error fix.
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

# Multiple market test cases as requested in the review
TEST_MARKET_CASES = {
    "fitness_tracker": {
        "product_name": "Fitness Tracker",
        "industry": "Wearable Technology", 
        "geography": "Global",
        "target_user": "Health-conscious consumers",
        "demand_driver": "Health and wellness trends",
        "transaction_type": "One-time Purchase",
        "key_metrics": "Device sales, user engagement",
        "benchmarks": "Market growing at 9.2% CAGR",
        "expected_competitors": ["Apple", "Fitbit", "Garmin"]
    },
    "saas_software": {
        "product_name": "SaaS Software for small businesses",
        "industry": "Software",
        "geography": "United States",
        "target_user": "Small business owners",
        "demand_driver": "Digital transformation and remote work",
        "transaction_type": "Subscription",
        "key_metrics": "Monthly recurring revenue, user adoption",
        "benchmarks": "SaaS market growing at 18% CAGR",
        "expected_competitors": ["Microsoft", "Salesforce", "HubSpot", "Slack"]
    },
    "ev_charging": {
        "product_name": "Electric Vehicle charging stations",
        "industry": "Energy & Infrastructure",
        "geography": "North America",
        "target_user": "EV owners and fleet operators",
        "demand_driver": "Electric vehicle adoption and government incentives",
        "transaction_type": "Usage-based pricing",
        "key_metrics": "Charging sessions, network utilization",
        "benchmarks": "EV charging market growing at 25% CAGR",
        "expected_competitors": ["Tesla", "ChargePoint", "EVgo", "Electrify America"]
    },
    "food_delivery": {
        "product_name": "Food delivery service",
        "industry": "Food & Beverage",
        "geography": "Urban markets",
        "target_user": "Busy professionals and families",
        "demand_driver": "Convenience and mobile app adoption",
        "transaction_type": "Commission-based",
        "key_metrics": "Order volume, delivery time, customer retention",
        "benchmarks": "Food delivery market growing at 12% CAGR",
        "expected_competitors": ["DoorDash", "Uber Eats", "Grubhub", "Postmates"]
    }
}

class EnhancedMarketMapAPITester:
    """Enhanced class to test the Market Map Generator API endpoints with focus on OpenAI JSON parsing fix"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.analysis_ids = {}
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def run_comprehensive_tests(self) -> bool:
        """Run comprehensive API tests focusing on OpenAI JSON parsing fix and multiple market categories"""
        tests = [
            ("API Health Check", self.test_api_health),
            ("Integration Status Check", self.test_integrations),
            ("Multiple Market Categories Analysis", self.test_multiple_market_categories),
            ("JSON Parsing Error Detection", self.test_json_parsing_errors),
            ("Analysis History", self.test_analysis_history),
            ("Export Functionality", self.test_export_functionality)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"Running Test: {test_name}")
            print(f"{'=' * 60}")
            
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
        
        # Print comprehensive summary
        print("\n\n")
        print(f"{'=' * 60}")
        print("COMPREHENSIVE TEST SUMMARY")
        print(f"{'=' * 60}")
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
    
    def test_integrations(self) -> Tuple[bool, str]:
        """Test the integrations status endpoint - focusing on OpenAI connection"""
        try:
            response = self.session.get(f"{self.api_url}/test-integrations")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            print(f"✅ Integration Status Response: {json.dumps(data, indent=2)}")
            
            # Check MongoDB status
            mongodb_status = data.get("integrations", {}).get("mongodb")
            if mongodb_status != "OK":
                return False, f"MongoDB integration failed: {mongodb_status}"
            
            # Check OpenAI status - should show connection status
            openai_status = data.get("integrations", {}).get("openai")
            print(f"🔍 OpenAI Status: {openai_status}")
            
            # Check if we have API version info
            api_version = data.get("api_version")
            if api_version != "2.0.0":
                return False, f"Expected API version 2.0.0, got {api_version}"
            
            return True, f"Integration status check passed - MongoDB: {mongodb_status}, OpenAI: {openai_status}"
        except Exception as e:
            return False, f"Integration status check failed: {str(e)}"
    
    def test_multiple_market_categories(self) -> Tuple[bool, str]:
        """Test market analysis with multiple different market categories"""
        results = []
        all_successful = True
        
        for category_name, market_data in TEST_MARKET_CASES.items():
            print(f"\n🔍 Testing Market Category: {category_name.upper()}")
            print(f"Product: {market_data['product_name']}")
            print(f"Industry: {market_data['industry']}")
            print(f"Geography: {market_data['geography']}")
            
            try:
                # Remove expected_competitors from the request data
                request_data = {k: v for k, v in market_data.items() if k != 'expected_competitors'}
                
                response = self.session.post(
                    f"{self.api_url}/analyze-market",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code != 200:
                    results.append(f"❌ {category_name}: HTTP {response.status_code}")
                    all_successful = False
                    continue
                
                data = response.json()
                
                # Validate response structure
                if not self._validate_market_analysis_structure(data):
                    results.append(f"❌ {category_name}: Invalid response structure")
                    all_successful = False
                    continue
                
                # Check for string formatting errors (the main issue we're testing for)
                if self._check_for_string_formatting_errors(data):
                    results.append(f"❌ {category_name}: String formatting errors detected")
                    all_successful = False
                    continue
                
                # Validate market data quality
                market_map = data.get("market_map", {})
                total_market_size = market_map.get("total_market_size", 0)
                competitors = market_map.get("competitors", [])
                
                # Check if we got reasonable market data
                if total_market_size <= 0:
                    results.append(f"❌ {category_name}: Invalid market size: {total_market_size}")
                    all_successful = False
                    continue
                
                if len(competitors) < 2:
                    results.append(f"❌ {category_name}: Insufficient competitors: {len(competitors)}")
                    all_successful = False
                    continue
                
                # Store analysis ID for later tests
                self.analysis_ids[category_name] = market_map.get("id")
                
                # Check for expected competitors (if any found)
                competitor_names = [comp.get("name", "") for comp in competitors]
                expected_competitors = market_data.get("expected_competitors", [])
                found_expected = [comp for comp in expected_competitors if any(comp in name for name in competitor_names)]
                
                print(f"  ✅ Market Size: ${total_market_size/1000000000:.1f}B")
                print(f"  ✅ Competitors Found: {len(competitors)}")
                print(f"  ✅ Expected Competitors Found: {found_expected}")
                print(f"  ✅ All Competitors: {competitor_names}")
                
                results.append(f"✅ {category_name}: Analysis successful")
                
            except requests.exceptions.Timeout:
                results.append(f"❌ {category_name}: Request timeout")
                all_successful = False
            except Exception as e:
                results.append(f"❌ {category_name}: {str(e)}")
                all_successful = False
        
        # Print results summary
        print(f"\n📊 MARKET CATEGORIES TEST RESULTS:")
        for result in results:
            print(f"  {result}")
        
        if all_successful:
            return True, f"All {len(TEST_MARKET_CASES)} market categories tested successfully"
        else:
            failed_count = len([r for r in results if r.startswith("❌")])
            return False, f"{failed_count}/{len(TEST_MARKET_CASES)} market categories failed"
    
    def test_json_parsing_errors(self) -> Tuple[bool, str]:
        """Specifically test for JSON parsing and string formatting errors"""
        print("🔍 Testing for JSON parsing and string formatting errors...")
        
        # Test with a market that might trigger edge cases
        edge_case_market = {
            "product_name": "AI-Powered Analytics Platform with {special} characters",
            "industry": "Artificial Intelligence & Machine Learning",
            "geography": "Global (including Asia-Pacific, Europe, Americas)",
            "target_user": "Data scientists and business analysts (25-45 years old)",
            "demand_driver": "AI adoption and data-driven decision making (>50% growth)",
            "transaction_type": "Subscription-based SaaS model",
            "key_metrics": "User engagement, model accuracy, processing speed",
            "benchmarks": "AI market growing at 35% CAGR with $500B+ TAM"
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=edge_case_market,
                timeout=30
            )
            
            if response.status_code != 200:
                return False, f"Edge case test failed with HTTP {response.status_code}: {response.text}"
            
            data = response.json()
            
            # Check for string formatting errors in the response
            formatting_errors = self._check_for_string_formatting_errors(data)
            if formatting_errors:
                return False, f"String formatting errors detected: {formatting_errors}"
            
            # Check for JSON structure integrity
            if not self._validate_market_analysis_structure(data):
                return False, "Invalid JSON structure in response"
            
            print("✅ No JSON parsing or string formatting errors detected")
            return True, "JSON parsing and string formatting test passed"
            
        except json.JSONDecodeError as e:
            return False, f"JSON decode error: {str(e)}"
        except Exception as e:
            return False, f"JSON parsing test failed: {str(e)}"
    
    def test_analysis_history(self) -> Tuple[bool, str]:
        """Test the analysis history endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/analysis-history")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            
            # Validate response structure
            if "history" not in data:
                return False, "Missing 'history' in response"
            
            history_count = len(data["history"])
            print(f"✅ Found {history_count} entries in analysis history")
            
            # If we have history, validate the structure
            if history_count > 0:
                first_entry = data["history"][0]
                required_fields = ["id", "product_name", "geography", "market_size", "timestamp"]
                for field in required_fields:
                    if field not in first_entry:
                        return False, f"Missing required field '{field}' in history entry"
            
            return True, f"Analysis history test passed with {history_count} entries"
        except Exception as e:
            return False, f"Analysis history test failed: {str(e)}"
    
    def test_export_functionality(self) -> Tuple[bool, str]:
        """Test the export functionality for multiple analyses"""
        if not self.analysis_ids:
            return False, "No analysis IDs available for export testing"
        
        successful_exports = 0
        total_exports = len(self.analysis_ids)
        
        for category, analysis_id in self.analysis_ids.items():
            if not analysis_id:
                continue
                
            try:
                response = self.session.get(
                    f"{self.api_url}/export-market-map/{analysis_id}",
                    stream=True,
                    timeout=30
                )
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type')
                    expected_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    if content_type == expected_type:
                        content_length = int(response.headers.get('Content-Length', 0))
                        print(f"  ✅ {category}: Export successful ({content_length} bytes)")
                        successful_exports += 1
                    else:
                        print(f"  ❌ {category}: Wrong content type: {content_type}")
                else:
                    print(f"  ❌ {category}: Export failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"  ❌ {category}: Export error: {str(e)}")
        
        if successful_exports == total_exports:
            return True, f"All {successful_exports} exports successful"
        else:
            return False, f"Only {successful_exports}/{total_exports} exports successful"
    
    def _validate_market_analysis_structure(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of market analysis response"""
        required_fields = ["market_input", "market_map", "visual_map"]
        for field in required_fields:
            if field not in data:
                print(f"❌ Missing required field: {field}")
                return False
        
        # Validate market_map structure
        market_map = data.get("market_map", {})
        market_map_fields = ["id", "total_market_size", "market_growth_rate", "competitors"]
        for field in market_map_fields:
            if field not in market_map:
                print(f"❌ Missing market_map field: {field}")
                return False
        
        return True
    
    def _check_for_string_formatting_errors(self, data: Dict[str, Any]) -> list:
        """Check for string formatting errors in the response data"""
        errors = []
        
        def check_string_recursive(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    check_string_recursive(value, f"{path}.{key}" if path else key)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_string_recursive(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                # Check for common string formatting errors
                if "{" in obj and "}" in obj and not obj.count("{") == obj.count("}"):
                    errors.append(f"Unmatched braces in {path}: {obj[:100]}")
                if "Invalid format specifier" in obj:
                    errors.append(f"Invalid format specifier in {path}: {obj[:100]}")
                if obj.startswith("Error:") or obj.startswith("ERROR:"):
                    errors.append(f"Error message in {path}: {obj[:100]}")
        
        check_string_recursive(data)
        return errors


if __name__ == "__main__":
    print("🚀 Starting Enhanced Market Map Generator API Tests")
    print("Focus: OpenAI JSON parsing fix and multiple market categories")
    print("=" * 60)
    
    tester = EnhancedMarketMapAPITester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("\n🎉 All comprehensive tests passed successfully!")
        print("✅ OpenAI JSON parsing fix verified")
        print("✅ Multiple market categories working")
        print("✅ No string formatting errors detected")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. See details above.")
        sys.exit(1)