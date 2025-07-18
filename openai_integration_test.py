#!/usr/bin/env python3
"""
OpenAI Integration Test for Market Map Generator
This script specifically tests that OpenAI is working and generating unique analysis
instead of falling back to curated database data.
"""

import requests
import json
import os
import sys
import time
from typing import Dict, Any, Optional, Tuple, List

# Get the backend URL from the frontend/.env file
def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

# Test cases for different market categories
TEST_MARKET_CATEGORIES = [
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
        },
        "curated_competitors": ["Apple", "Fitbit", "Garmin"]  # These should NOT appear if OpenAI is working
    },
    {
        "name": "SaaS Software for Small Businesses",
        "data": {
            "product_name": "SaaS Software for small businesses",
            "industry": "Software",
            "geography": "United States",
            "target_user": "Small business owners",
            "demand_driver": "Digital transformation",
            "transaction_type": "Subscription",
            "key_metrics": "Monthly recurring revenue, user adoption",
            "benchmarks": "SaaS market growing at 18% CAGR"
        },
        "curated_competitors": []  # No curated data for this category
    },
    {
        "name": "Electric Vehicle Charging Stations",
        "data": {
            "product_name": "Electric Vehicle charging stations",
            "industry": "Energy",
            "geography": "North America",
            "target_user": "EV owners and fleet operators",
            "demand_driver": "EV adoption and government incentives",
            "transaction_type": "Usage-based",
            "key_metrics": "Charging sessions, revenue per station",
            "benchmarks": "EV charging market growing at 25% CAGR"
        },
        "curated_competitors": []  # No curated data for this category
    },
    {
        "name": "Food Delivery Service",
        "data": {
            "product_name": "Food delivery service",
            "industry": "Food & Beverage",
            "geography": "Urban markets",
            "target_user": "Busy professionals and families",
            "demand_driver": "Convenience and time-saving",
            "transaction_type": "Commission-based",
            "key_metrics": "Order volume, delivery time, customer retention",
            "benchmarks": "Food delivery market growing at 12% CAGR"
        },
        "curated_competitors": []  # No curated data for this category
    }
]

class OpenAIIntegrationTester:
    """Class to test OpenAI integration and verify unique analysis generation"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.analysis_results = []
        print(f"Using API URL: {self.api_url}")
    
    def run_openai_integration_tests(self) -> bool:
        """Run comprehensive OpenAI integration tests"""
        print(f"\n{'=' * 60}")
        print("OPENAI INTEGRATION TEST SUITE")
        print(f"{'=' * 60}")
        
        # Step 1: Test OpenAI connection
        print(f"\n{'=' * 50}")
        print("Step 1: Testing OpenAI Connection")
        print(f"{'=' * 50}")
        
        openai_working, openai_message = self.test_openai_connection()
        if not openai_working:
            print(f"❌ OpenAI connection failed: {openai_message}")
            return False
        
        print(f"✅ OpenAI connection successful: {openai_message}")
        
        # Step 2: Test unique analysis generation
        print(f"\n{'=' * 50}")
        print("Step 2: Testing Unique Analysis Generation")
        print(f"{'=' * 50}")
        
        all_passed = True
        for test_case in TEST_MARKET_CATEGORIES:
            print(f"\n--- Testing: {test_case['name']} ---")
            
            success, message, analysis_data = self.test_market_analysis(test_case)
            if not success:
                print(f"❌ {test_case['name']}: {message}")
                all_passed = False
            else:
                print(f"✅ {test_case['name']}: {message}")
                self.analysis_results.append({
                    "category": test_case['name'],
                    "data": analysis_data
                })
        
        # Step 3: Verify uniqueness across categories
        print(f"\n{'=' * 50}")
        print("Step 3: Verifying Analysis Uniqueness")
        print(f"{'=' * 50}")
        
        uniqueness_passed, uniqueness_message = self.verify_analysis_uniqueness()
        if not uniqueness_passed:
            print(f"❌ Uniqueness check failed: {uniqueness_message}")
            all_passed = False
        else:
            print(f"✅ Uniqueness check passed: {uniqueness_message}")
        
        # Step 4: Verify no fallback to curated data
        print(f"\n{'=' * 50}")
        print("Step 4: Verifying No Curated Data Fallback")
        print(f"{'=' * 50}")
        
        fallback_passed, fallback_message = self.verify_no_curated_fallback()
        if not fallback_passed:
            print(f"❌ Curated data fallback detected: {fallback_message}")
            all_passed = False
        else:
            print(f"✅ No curated data fallback: {fallback_message}")
        
        return all_passed
    
    def test_openai_connection(self) -> Tuple[bool, str]:
        """Test if OpenAI connection is working"""
        try:
            response = self.session.get(f"{self.api_url}/test-integrations")
            if response.status_code != 200:
                return False, f"API call failed with status {response.status_code}"
            
            data = response.json()
            openai_status = data.get("integrations", {}).get("openai", "Unknown")
            
            print(f"OpenAI Status: {openai_status}")
            
            # Check if OpenAI is working (should be "OK" if API key is valid)
            if openai_status == "OK":
                return True, "OpenAI connection is working"
            elif "Failed" in openai_status:
                return False, f"OpenAI connection failed: {openai_status}"
            else:
                return False, f"Unexpected OpenAI status: {openai_status}"
                
        except Exception as e:
            return False, f"Error testing OpenAI connection: {str(e)}"
    
    def test_market_analysis(self, test_case: Dict[str, Any]) -> Tuple[bool, str, Optional[Dict]]:
        """Test market analysis for a specific category"""
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=test_case["data"]
            )
            
            if response.status_code != 200:
                return False, f"API call failed with status {response.status_code}", None
            
            data = response.json()
            
            # Validate response structure
            if "market_map" not in data:
                return False, "Missing market_map in response", None
            
            market_map = data["market_map"]
            
            # Check for competitors
            competitors = market_map.get("competitors", [])
            if not competitors:
                return False, "No competitors found in analysis", None
            
            competitor_names = [comp.get("name", "") for comp in competitors]
            
            # Check if we got real analysis (should have at least 3 competitors)
            if len(competitors) < 3:
                return False, f"Too few competitors ({len(competitors)}), likely fallback data", None
            
            # Check market size (should not be generic $1B or $5B fallback)
            market_size = market_map.get("total_market_size", 0)
            if market_size in [1000000000, 5000000000]:  # $1B or $5B fallback values
                return False, f"Generic market size detected (${market_size/1000000000:.0f}B), likely fallback", None
            
            # Check confidence level (should be higher than "low" if OpenAI is working)
            confidence = market_map.get("confidence_level", "unknown")
            if confidence == "low":
                return False, "Low confidence level suggests fallback analysis", None
            
            print(f"  Competitors: {competitor_names[:5]}...")  # Show first 5
            print(f"  Market Size: ${market_size/1000000000:.1f}B")
            print(f"  Confidence: {confidence}")
            print(f"  Growth Rate: {market_map.get('market_growth_rate', 0)*100:.1f}%")
            
            return True, f"Generated analysis with {len(competitors)} competitors", data
            
        except Exception as e:
            return False, f"Error during market analysis: {str(e)}", None
    
    def verify_analysis_uniqueness(self) -> Tuple[bool, str]:
        """Verify that different market categories get different analysis"""
        if len(self.analysis_results) < 2:
            return False, "Not enough analysis results to compare uniqueness"
        
        # Compare competitors across different categories
        competitor_sets = []
        market_sizes = []
        
        for result in self.analysis_results:
            market_map = result["data"]["market_map"]
            competitors = [comp.get("name", "") for comp in market_map.get("competitors", [])]
            competitor_sets.append(set(competitors))
            market_sizes.append(market_map.get("total_market_size", 0))
        
        # Check if competitor sets are different
        unique_competitors = True
        for i in range(len(competitor_sets)):
            for j in range(i + 1, len(competitor_sets)):
                overlap = len(competitor_sets[i].intersection(competitor_sets[j]))
                total_unique = len(competitor_sets[i].union(competitor_sets[j]))
                overlap_percentage = (overlap / total_unique) * 100 if total_unique > 0 else 0
                
                print(f"  {self.analysis_results[i]['category']} vs {self.analysis_results[j]['category']}: {overlap_percentage:.1f}% overlap")
                
                # If more than 50% overlap, it might be using similar data
                if overlap_percentage > 50:
                    unique_competitors = False
        
        # Check if market sizes are different
        unique_sizes = len(set(market_sizes)) == len(market_sizes)
        
        if unique_competitors and unique_sizes:
            return True, "Analysis shows good uniqueness across categories"
        elif not unique_competitors:
            return False, "High overlap in competitors suggests non-unique analysis"
        else:
            return False, "Similar market sizes suggest generic analysis"
    
    def verify_no_curated_fallback(self) -> Tuple[bool, str]:
        """Verify that the system is not using curated database fallback"""
        # Check specifically for fitness tracker analysis
        fitness_analysis = None
        for result in self.analysis_results:
            if "Fitness Tracker" in result["category"]:
                fitness_analysis = result
                break
        
        if not fitness_analysis:
            return True, "No fitness tracker analysis to check for curated fallback"
        
        # Check if fitness tracker analysis contains the curated competitors
        market_map = fitness_analysis["data"]["market_map"]
        competitors = [comp.get("name", "") for comp in market_map.get("competitors", [])]
        
        curated_competitors = ["Apple", "Fitbit", "Garmin"]
        found_curated = [comp for comp in curated_competitors if comp in competitors]
        
        print(f"  Fitness Tracker Competitors: {competitors}")
        print(f"  Curated Competitors Found: {found_curated}")
        
        # If we find the exact curated set, it's likely fallback
        if len(found_curated) >= 2:  # Allow some flexibility
            return False, f"Found curated competitors {found_curated}, suggesting fallback to curated database"
        
        # Check methodology - should not mention "fallback"
        methodology = market_map.get("methodology", "").lower()
        if "fallback" in methodology or "minimal" in methodology:
            return False, f"Methodology suggests fallback: {methodology}"
        
        return True, "No evidence of curated database fallback"
    
    def print_detailed_summary(self):
        """Print detailed summary of all analysis results"""
        print(f"\n{'=' * 60}")
        print("DETAILED ANALYSIS SUMMARY")
        print(f"{'=' * 60}")
        
        for result in self.analysis_results:
            print(f"\n--- {result['category']} ---")
            market_map = result["data"]["market_map"]
            
            print(f"Market Size: ${market_map.get('total_market_size', 0)/1000000000:.1f}B")
            print(f"Growth Rate: {market_map.get('market_growth_rate', 0)*100:.1f}%")
            print(f"Confidence: {market_map.get('confidence_level', 'unknown')}")
            print(f"Methodology: {market_map.get('methodology', 'unknown')}")
            
            competitors = market_map.get("competitors", [])
            print(f"Competitors ({len(competitors)}):")
            for comp in competitors[:5]:  # Show first 5
                print(f"  - {comp.get('name', 'Unknown')}")
            if len(competitors) > 5:
                print(f"  ... and {len(competitors) - 5} more")


if __name__ == "__main__":
    print("Starting OpenAI Integration Tests for Market Map Generator")
    tester = OpenAIIntegrationTester()
    
    success = tester.run_openai_integration_tests()
    
    # Print detailed summary
    tester.print_detailed_summary()
    
    if success:
        print(f"\n{'=' * 60}")
        print("✅ ALL OPENAI INTEGRATION TESTS PASSED!")
        print("✅ OpenAI is working and generating unique analysis")
        print("✅ No fallback to curated database detected")
        print(f"{'=' * 60}")
        sys.exit(0)
    else:
        print(f"\n{'=' * 60}")
        print("❌ SOME OPENAI INTEGRATION TESTS FAILED!")
        print("❌ Check the detailed results above")
        print(f"{'=' * 60}")
        sys.exit(1)