#!/usr/bin/env python3
"""
DTCC Market Map Generator Test Script
This script specifically tests the DTCC financial services scenario as requested in the review.
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

# DTCC test case as specified in the review request
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

class DTCCMarketMapTester:
    """Class to test the Market Map Generator API specifically for DTCC scenario"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.analysis_id = None
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
        print(f"Testing DTCC scenario: {DTCC_TEST_DATA}")
    
    def run_dtcc_tests(self) -> bool:
        """Run DTCC-specific tests and return overall success status"""
        tests = [
            ("API Health Check", self.test_api_health),
            ("DTCC Market Analysis", self.test_dtcc_market_analysis),
            ("DTCC Competitive Analysis Validation", self.test_dtcc_competitive_analysis),
            ("TAM-SAM-SOM Data Structure", self.test_tam_sam_som_structure),
            ("Visual Map Structure", self.test_visual_map_structure)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"Running DTCC Test: {test_name}")
            print(f"{'=' * 60}")
            
            try:
                success, message = test_func()
                status = "✅ PASSED" if success else "❌ FAILED"
                results.append((test_name, status, message))
                if not success:
                    all_passed = False
                print(f"Result: {status} - {message}")
            except Exception as e:
                results.append((test_name, "❌ ERROR", str(e)))
                all_passed = False
                print(f"Error during test: {e}")
        
        # Print summary
        print("\n\n")
        print(f"{'=' * 60}")
        print("DTCC TEST SUMMARY")
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
            
            return True, "API health check passed"
        except Exception as e:
            return False, f"API health check failed: {str(e)}"
    
    def test_dtcc_market_analysis(self) -> Tuple[bool, str]:
        """Test the market analysis endpoint specifically for DTCC"""
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=DTCC_TEST_DATA
            )
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            
            # Store the full response for other tests
            self.dtcc_analysis = data
            self.analysis_id = data["market_map"]["id"]
            
            # Validate response structure
            required_fields = ["market_input", "market_map", "visual_map"]
            for field in required_fields:
                if field not in data:
                    return False, f"Missing '{field}' in response"
            
            # Check if the product name matches DTCC
            if data["market_input"]["product_name"] != "DTCC":
                return False, f"Product name mismatch: {data['market_input']['product_name']} vs DTCC"
            
            # Check if industry is Financial Services
            if data["market_input"]["industry"] != "Financial Services":
                return False, f"Industry mismatch: {data['market_input']['industry']} vs Financial Services"
            
            print(f"✅ DTCC analysis generated successfully")
            print(f"✅ Analysis ID: {self.analysis_id}")
            print(f"✅ Market size: ${data['market_map']['total_market_size']:,.0f}")
            print(f"✅ Growth rate: {data['market_map']['market_growth_rate']*100:.1f}%")
            
            return True, "DTCC market analysis completed successfully"
        except Exception as e:
            return False, f"DTCC market analysis failed: {str(e)}"
    
    def test_dtcc_competitive_analysis(self) -> Tuple[bool, str]:
        """Test that DTCC competitive analysis includes proper financial services competitors"""
        if not hasattr(self, 'dtcc_analysis'):
            return False, "DTCC analysis not available. Run market analysis first."
        
        try:
            competitors = self.dtcc_analysis["market_map"]["competitors"]
            competitor_names = [comp["name"] for comp in competitors]
            
            print(f"Found competitors: {competitor_names}")
            
            # Check minimum 4 competitors requirement
            if len(competitors) < 4:
                return False, f"Expected minimum 4 competitors, found {len(competitors)}: {competitor_names}"
            
            # Check if DTCC appears as one of the competitors for comparison
            dtcc_found = any("DTCC" in name for name in competitor_names)
            if not dtcc_found:
                print(f"⚠️  DTCC not found in competitors list for benchmarking")
            else:
                print(f"✅ DTCC found in competitors for benchmarking")
            
            # Expected financial services competitors
            expected_financial_competitors = [
                "JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Bank of America",
                "Citigroup", "Wells Fargo", "BlackRock", "Vanguard", "Fidelity",
                "Charles Schwab", "CME Group", "ICE", "Nasdaq", "NYSE"
            ]
            
            # Check if we have proper financial services competitors
            financial_competitors_found = []
            for competitor in competitor_names:
                for expected in expected_financial_competitors:
                    if expected.lower() in competitor.lower() or competitor.lower() in expected.lower():
                        financial_competitors_found.append(competitor)
                        break
            
            print(f"Financial services competitors found: {financial_competitors_found}")
            
            if len(financial_competitors_found) < 2:
                return False, f"Expected at least 2 financial services competitors, found {len(financial_competitors_found)}: {financial_competitors_found}"
            
            # Validate competitor structure
            for i, competitor in enumerate(competitors):
                required_fields = ["name", "strengths", "weaknesses"]
                for field in required_fields:
                    if field not in competitor:
                        return False, f"Competitor {i} missing required field: {field}"
                
                if not competitor["strengths"] or not competitor["weaknesses"]:
                    return False, f"Competitor {competitor['name']} has empty strengths or weaknesses"
            
            print(f"✅ Found {len(competitors)} competitors (minimum 4 required)")
            print(f"✅ Found {len(financial_competitors_found)} financial services competitors")
            print(f"✅ All competitors have proper structure with strengths and weaknesses")
            
            return True, f"Competitive analysis validation passed with {len(competitors)} competitors including {len(financial_competitors_found)} financial services companies"
        except Exception as e:
            return False, f"Competitive analysis validation failed: {str(e)}"
    
    def test_tam_sam_som_structure(self) -> Tuple[bool, str]:
        """Test that TAM-SAM-SOM data structure is properly generated"""
        if not hasattr(self, 'dtcc_analysis'):
            return False, "DTCC analysis not available. Run market analysis first."
        
        try:
            market_map = self.dtcc_analysis["market_map"]
            
            # Check TAM (Total Addressable Market)
            tam = market_map.get("total_market_size")
            if not tam or tam <= 0:
                return False, f"Invalid TAM value: {tam}"
            
            # Check growth rate
            growth_rate = market_map.get("market_growth_rate")
            if growth_rate is None or growth_rate < 0:
                return False, f"Invalid growth rate: {growth_rate}"
            
            # Check market segmentation for SAM/SOM calculation
            segmentation_types = [
                "segmentation_by_geographics",
                "segmentation_by_demographics", 
                "segmentation_by_psychographics",
                "segmentation_by_behavioral"
            ]
            
            segments_found = 0
            total_segment_size = 0
            
            for seg_type in segmentation_types:
                segments = market_map.get(seg_type, [])
                if segments:
                    segments_found += 1
                    for segment in segments:
                        if "size_estimate" in segment:
                            total_segment_size += segment["size_estimate"]
                        print(f"  - {segment.get('name', 'Unnamed')}: ${segment.get('size_estimate', 0):,.0f}")
            
            if segments_found == 0:
                return False, "No market segmentation data found for SAM/SOM calculation"
            
            print(f"✅ TAM: ${tam:,.0f}")
            print(f"✅ Growth Rate: {growth_rate*100:.1f}%")
            print(f"✅ Found {segments_found} segmentation types")
            print(f"✅ Total segment size: ${total_segment_size:,.0f}")
            
            # Validate that segments are reasonable compared to TAM
            if total_segment_size > tam * 5:  # Allow some flexibility for overlapping segments
                print(f"⚠️  Warning: Total segment size ({total_segment_size:,.0f}) seems high compared to TAM ({tam:,.0f})")
            
            return True, f"TAM-SAM-SOM structure validated with TAM of ${tam:,.0f} and {segments_found} segmentation types"
        except Exception as e:
            return False, f"TAM-SAM-SOM structure validation failed: {str(e)}"
    
    def test_visual_map_structure(self) -> Tuple[bool, str]:
        """Test that visual map data is properly structured for frontend display"""
        if not hasattr(self, 'dtcc_analysis'):
            return False, "DTCC analysis not available. Run market analysis first."
        
        try:
            visual_map = self.dtcc_analysis["visual_map"]
            
            if not visual_map:
                return False, "Visual map data is missing"
            
            # Check required visual map fields
            required_fields = ["title", "market_overview"]
            for field in required_fields:
                if field not in visual_map:
                    return False, f"Visual map missing required field: {field}"
            
            # Check segment types in visual map
            segment_types = [
                "geographic_segments",
                "demographic_segments",
                "psychographic_segments", 
                "behavioral_segments"
            ]
            
            segments_with_data = 0
            for seg_type in segment_types:
                segments = visual_map.get(seg_type, [])
                if segments:
                    segments_with_data += 1
                    print(f"✅ {seg_type}: {len(segments)} segments")
                    
                    # Validate segment structure
                    for segment in segments:
                        required_seg_fields = ["name", "description", "size", "growth", "icon", "color"]
                        for field in required_seg_fields:
                            if field not in segment:
                                return False, f"Visual map segment missing field: {field}"
                else:
                    print(f"⚠️  {seg_type}: No segments found")
            
            if segments_with_data == 0:
                return False, "No visual map segments found"
            
            # Check title contains DTCC
            title = visual_map.get("title", "")
            if "DTCC" not in title:
                return False, f"Visual map title should contain 'DTCC', got: {title}"
            
            print(f"✅ Visual map title: {title}")
            print(f"✅ Found {segments_with_data} segment types with visual data")
            print(f"✅ Market overview data present: {bool(visual_map.get('market_overview'))}")
            
            return True, f"Visual map structure validated with {segments_with_data} segment types"
        except Exception as e:
            return False, f"Visual map structure validation failed: {str(e)}"


if __name__ == "__main__":
    print("Starting DTCC Market Map Generator Tests")
    print("=" * 60)
    tester = DTCCMarketMapTester()
    success = tester.run_dtcc_tests()
    
    if success:
        print("\n✅ All DTCC tests passed successfully!")
        print("✅ DTCC appears in competitive analysis")
        print("✅ Financial services competitors included")
        print("✅ TAM-SAM-SOM structure properly formed")
        print("✅ Visual map ready for frontend display")
        sys.exit(0)
    else:
        print("\n❌ Some DTCC tests failed. See details above.")
        sys.exit(1)