#!/usr/bin/env python3
"""
Resonate rAI Persona Export Functionality Test Script
Tests the new enhanced segmentation and export functionality for Resonate integration.
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

# Sample market data for testing Resonate functionality
SMART_FITNESS_TRACKER_DATA = {
    "product_name": "Smart Fitness Tracker",
    "industry": "Wearable Technology", 
    "geography": "United States",
    "target_user": "Health-conscious millennials and Gen Z",
    "demand_driver": "Growing health awareness and fitness tracking trends",
    "transaction_type": "One-time Purchase with Subscription Services",
    "key_metrics": "Device sales, monthly active users, subscription retention",
    "benchmarks": "Wearable market growing at 13.8% CAGR, 35% of adults use fitness trackers"
}

class ResonateAPITester:
    """Class to test the Resonate rAI persona export functionality"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.analysis_id = None
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def run_all_tests(self) -> bool:
        """Run all Resonate-specific tests and return overall success status"""
        tests = [
            ("API Health Check", self.test_api_health),
            ("Market Analysis with Enhanced Segmentation", self.test_enhanced_market_analysis),
            ("Export Personas Endpoint", self.test_export_personas),
            ("Validate Resonate Taxonomy Mapping", self.test_resonate_taxonomy_mapping),
            ("Test Data Structure", self.test_data_structure),
            ("Test Backward Compatibility", self.test_backward_compatibility)
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
        
        # Print summary
        print("\n\n")
        print(f"{'=' * 60}")
        print("RESONATE FUNCTIONALITY TEST SUMMARY")
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
            
            print(f"API Health Response: {data}")
            return True, "API health check passed"
        except Exception as e:
            return False, f"API health check failed: {str(e)}"
    
    def test_enhanced_market_analysis(self) -> Tuple[bool, str]:
        """Test market analysis with enhanced segmentation for Resonate mapping"""
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=SMART_FITNESS_TRACKER_DATA
            )
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            print(f"Enhanced Market Analysis Response Structure:")
            print(f"- market_input: {'✓' if 'market_input' in data else '✗'}")
            print(f"- market_map: {'✓' if 'market_map' in data else '✗'}")
            print(f"- visual_map: {'✓' if 'visual_map' in data else '✗'}")
            
            # Validate enhanced segmentation structure
            market_map = data.get("market_map", {})
            
            # Check for demographic segments with resonate_mapping
            demographic_segments = market_map.get("segmentation_by_demographics", [])
            psychographic_segments = market_map.get("segmentation_by_psychographics", [])
            behavioral_segments = market_map.get("segmentation_by_behavioral", [])
            
            print(f"\nSegmentation Analysis:")
            print(f"- Demographic segments: {len(demographic_segments)}")
            print(f"- Psychographic segments: {len(psychographic_segments)}")
            print(f"- Behavioral segments: {len(behavioral_segments)}")
            
            # Check for resonate_mapping in segments
            resonate_mappings_found = 0
            for segment in demographic_segments + psychographic_segments + behavioral_segments:
                if "resonate_mapping" in segment:
                    resonate_mappings_found += 1
                    mapping = segment["resonate_mapping"]
                    print(f"\nFound Resonate mapping in segment '{segment.get('name')}':")
                    print(f"  - Demographics: {'✓' if mapping.get('demographics') else '✗'}")
                    print(f"  - Geographics: {'✓' if mapping.get('geographics') else '✗'}")
                    print(f"  - Media Usage: {'✓' if mapping.get('media_usage') else '✗'}")
                    print(f"  - Taxonomy Paths: {len(mapping.get('resonate_taxonomy_paths', []))} paths")
                    print(f"  - Confidence: {mapping.get('mapping_confidence', 'N/A')}")
            
            if resonate_mappings_found == 0:
                return False, "No resonate_mapping data found in any segments"
            
            # Store analysis ID for export test
            self.analysis_id = market_map.get("id")
            print(f"\nStored analysis ID for export test: {self.analysis_id}")
            
            return True, f"Enhanced market analysis passed with {resonate_mappings_found} Resonate mappings"
        except Exception as e:
            return False, f"Enhanced market analysis test failed: {str(e)}"
    
    def test_export_personas(self) -> Tuple[bool, str]:
        """Test the new /api/export-personas/{analysis_id} endpoint"""
        if not self.analysis_id:
            print("No analysis ID available, running market analysis first...")
            success, _ = self.test_enhanced_market_analysis()
            if not success:
                return False, "Failed to get analysis ID for export test"
        
        try:
            response = self.session.get(f"{self.api_url}/export-personas/{self.analysis_id}")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            print(f"Export Personas Response Structure:")
            
            # Validate response structure
            required_fields = [
                "analysis_info", "demographic_personas", "psychographic_personas", 
                "behavioral_personas", "resonate_taxonomy_mapping", "persona_summary"
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in data:
                    missing_fields.append(field)
                else:
                    print(f"- {field}: ✓")
            
            if missing_fields:
                return False, f"Missing required fields: {missing_fields}"
            
            # Validate analysis_info
            analysis_info = data["analysis_info"]
            if analysis_info.get("product_name") != SMART_FITNESS_TRACKER_DATA["product_name"]:
                return False, f"Product name mismatch in analysis_info"
            
            # Count personas and mappings
            demographic_count = len(data["demographic_personas"])
            psychographic_count = len(data["psychographic_personas"])
            behavioral_count = len(data["behavioral_personas"])
            mapping_count = len(data["resonate_taxonomy_mapping"])
            
            print(f"\nPersona Counts:")
            print(f"- Demographic personas: {demographic_count}")
            print(f"- Psychographic personas: {psychographic_count}")
            print(f"- Behavioral personas: {behavioral_count}")
            print(f"- Resonate taxonomy mappings: {mapping_count}")
            
            # Validate persona summary
            summary = data["persona_summary"]
            expected_total = demographic_count + psychographic_count + behavioral_count
            if summary.get("total_segments") != expected_total:
                return False, f"Persona summary total_segments mismatch: {summary.get('total_segments')} vs {expected_total}"
            
            print(f"\nPersona Summary:")
            print(f"- Total segments: {summary.get('total_segments')}")
            print(f"- Resonate ready segments: {summary.get('resonate_ready_segments')}")
            print(f"- Total taxonomy mappings: {summary.get('total_taxonomy_mappings')}")
            print(f"- Resonate integration ready: {summary.get('resonate_integration_ready')}")
            
            return True, f"Export personas endpoint passed with {mapping_count} Resonate mappings"
        except Exception as e:
            return False, f"Export personas test failed: {str(e)}"
    
    def test_resonate_taxonomy_mapping(self) -> Tuple[bool, str]:
        """Validate that exported data includes proper Resonate Elements taxonomy paths"""
        if not self.analysis_id:
            return False, "No analysis ID available for taxonomy mapping test"
        
        try:
            response = self.session.get(f"{self.api_url}/export-personas/{self.analysis_id}")
            if response.status_code != 200:
                return False, f"Failed to get export data: {response.status_code}"
            
            data = response.json()
            mappings = data.get("resonate_taxonomy_mapping", [])
            
            if not mappings:
                return False, "No Resonate taxonomy mappings found"
            
            print(f"Validating {len(mappings)} taxonomy mappings...")
            
            # Expected taxonomy path patterns
            expected_patterns = [
                "Demographics > Demographics > Identity > Age Group",
                "Demographics > Demographics > Identity > Gender",
                "Demographics > Demographics > SocioEconomic > Household Income",
                "Demographics > Demographics > SocioEconomic > Education",
                "Media > Media Consumption > Digital Engagement"
            ]
            
            found_patterns = set()
            valid_mappings = 0
            
            for mapping in mappings:
                segment_name = mapping.get("segment_name", "Unknown")
                taxonomy_paths = mapping.get("taxonomy_paths", [])
                
                print(f"\nSegment: {segment_name}")
                print(f"  Taxonomy paths ({len(taxonomy_paths)}):")
                
                for path in taxonomy_paths:
                    print(f"    - {path}")
                    # Check if path matches expected patterns
                    for pattern in expected_patterns:
                        if pattern in path:
                            found_patterns.add(pattern)
                
                # Validate mapping structure
                demographics = mapping.get("demographics", {})
                geographics = mapping.get("geographics", {})
                media_usage = mapping.get("media_usage", {})
                
                if demographics or geographics or media_usage:
                    valid_mappings += 1
                    print(f"  Demographics: {list(demographics.keys()) if demographics else 'None'}")
                    print(f"  Geographics: {list(geographics.keys()) if geographics else 'None'}")
                    print(f"  Media Usage: {list(media_usage.keys()) if media_usage else 'None'}")
                    print(f"  Confidence: {mapping.get('confidence', 'N/A')}")
            
            print(f"\nTaxonomy Validation Results:")
            print(f"- Valid mappings with data: {valid_mappings}/{len(mappings)}")
            print(f"- Expected patterns found: {len(found_patterns)}/{len(expected_patterns)}")
            print(f"- Found patterns: {list(found_patterns)}")
            
            if valid_mappings == 0:
                return False, "No valid Resonate mappings with demographic/geographic/media data found"
            
            if len(found_patterns) < 2:
                return False, f"Insufficient taxonomy pattern coverage: {len(found_patterns)} patterns found"
            
            return True, f"Taxonomy mapping validation passed: {valid_mappings} valid mappings, {len(found_patterns)} taxonomy patterns"
        except Exception as e:
            return False, f"Taxonomy mapping validation failed: {str(e)}"
    
    def test_data_structure(self) -> Tuple[bool, str]:
        """Test that the new simplified structure focuses on base-level data"""
        if not self.analysis_id:
            return False, "No analysis ID available for data structure test"
        
        try:
            response = self.session.get(f"{self.api_url}/export-personas/{self.analysis_id}")
            if response.status_code != 200:
                return False, f"Failed to get export data: {response.status_code}"
            
            data = response.json()
            mappings = data.get("resonate_taxonomy_mapping", [])
            
            print("Validating simplified data structure for base-level data...")
            
            # Expected base-level data fields
            expected_demographic_fields = ["age_range", "gender", "household_income", "education", "employment"]
            expected_geographic_fields = ["region", "market_size", "geography_type"]
            expected_media_fields = ["primary_media", "digital_engagement", "content_preferences"]
            
            found_demographic_fields = set()
            found_geographic_fields = set()
            found_media_fields = set()
            
            for mapping in mappings:
                demographics = mapping.get("demographics", {})
                geographics = mapping.get("geographics", {})
                media_usage = mapping.get("media_usage", {})
                
                # Check demographic fields
                for field in expected_demographic_fields:
                    if field in demographics and demographics[field]:
                        found_demographic_fields.add(field)
                
                # Check geographic fields
                for field in expected_geographic_fields:
                    if field in geographics and geographics[field]:
                        found_geographic_fields.add(field)
                
                # Check media usage fields
                for field in expected_media_fields:
                    if field in media_usage and media_usage[field]:
                        found_media_fields.add(field)
            
            print(f"\nBase-level Data Coverage:")
            print(f"Demographics ({len(found_demographic_fields)}/{len(expected_demographic_fields)}):")
            for field in expected_demographic_fields:
                status = "✓" if field in found_demographic_fields else "✗"
                print(f"  {status} {field}")
            
            print(f"Geographics ({len(found_geographic_fields)}/{len(expected_geographic_fields)}):")
            for field in expected_geographic_fields:
                status = "✓" if field in found_geographic_fields else "✗"
                print(f"  {status} {field}")
            
            print(f"Media Usage ({len(found_media_fields)}/{len(expected_media_fields)}):")
            for field in expected_media_fields:
                status = "✓" if field in found_media_fields else "✗"
                print(f"  {status} {field}")
            
            # Validate that we have reasonable coverage
            demographic_coverage = len(found_demographic_fields) / len(expected_demographic_fields)
            geographic_coverage = len(found_geographic_fields) / len(expected_geographic_fields)
            media_coverage = len(found_media_fields) / len(expected_media_fields)
            
            if demographic_coverage < 0.6:  # At least 60% coverage
                return False, f"Insufficient demographic field coverage: {demographic_coverage:.1%}"
            
            if geographic_coverage < 0.5:  # At least 50% coverage
                return False, f"Insufficient geographic field coverage: {geographic_coverage:.1%}"
            
            return True, f"Data structure validation passed: Demographics {demographic_coverage:.1%}, Geographics {geographic_coverage:.1%}, Media {media_coverage:.1%}"
        except Exception as e:
            return False, f"Data structure test failed: {str(e)}"
    
    def test_backward_compatibility(self) -> Tuple[bool, str]:
        """Test that existing analyses still work and new resonate_mapping data is optional"""
        try:
            # Test analysis history endpoint
            response = self.session.get(f"{self.api_url}/analysis-history")
            if response.status_code != 200:
                return False, f"Analysis history endpoint failed: {response.status_code}"
            
            history_data = response.json()
            history = history_data.get("history", [])
            
            print(f"Found {len(history)} historical analyses")
            
            if len(history) == 0:
                print("No historical analyses to test backward compatibility")
                return True, "Backward compatibility test passed (no historical data)"
            
            # Test loading an older analysis
            older_analysis = history[0] if history else None
            if older_analysis:
                older_id = older_analysis["id"]
                print(f"Testing backward compatibility with analysis ID: {older_id}")
                
                # Test get_analysis endpoint
                response = self.session.get(f"{self.api_url}/get-analysis/{older_id}")
                if response.status_code != 200:
                    return False, f"Failed to load older analysis: {response.status_code}"
                
                older_data = response.json()
                print("✓ Successfully loaded older analysis")
                
                # Test export-personas with older analysis (should handle missing resonate_mapping gracefully)
                response = self.session.get(f"{self.api_url}/export-personas/{older_id}")
                if response.status_code != 200:
                    return False, f"Export personas failed for older analysis: {response.status_code}"
                
                export_data = response.json()
                print("✓ Successfully exported personas from older analysis")
                
                # Check that the response structure is still valid even without resonate_mapping
                required_fields = ["analysis_info", "demographic_personas", "persona_summary"]
                for field in required_fields:
                    if field not in export_data:
                        return False, f"Missing required field '{field}' in backward compatibility test"
                
                print("✓ Backward compatibility structure validation passed")
            
            return True, "Backward compatibility test passed - existing analyses work correctly"
        except Exception as e:
            return False, f"Backward compatibility test failed: {str(e)}"


if __name__ == "__main__":
    print("Starting Resonate rAI Persona Export Functionality Tests")
    print("=" * 60)
    tester = ResonateAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All Resonate functionality tests passed successfully!")
        print("The Market Map Generator is ready for Resonate rAI integration.")
        sys.exit(0)
    else:
        print("\n❌ Some Resonate functionality tests failed. See details above.")
        sys.exit(1)