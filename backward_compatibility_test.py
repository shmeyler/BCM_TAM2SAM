#!/usr/bin/env python3
"""
Backward Compatibility Test for Market Map Generator
Tests the fix for older reports missing new fields (analysis_perspective, brand_position, segmentation_by_firmographics)
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

class BackwardCompatibilityTester:
    """Test backward compatibility for older reports"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def run_backward_compatibility_tests(self) -> bool:
        """Run all backward compatibility tests"""
        tests = [
            ("Analysis History Retrieval", self.test_analysis_history_retrieval),
            ("Multiple Analysis ID Loading", self.test_multiple_analysis_loading),
            ("Default Values for Missing Fields", self.test_default_values),
            ("Visual Map Generation Compatibility", self.test_visual_map_compatibility),
            ("Mixed Old and New Analysis Retrieval", self.test_mixed_analysis_retrieval)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"Running Backward Compatibility Test: {test_name}")
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
        print("BACKWARD COMPATIBILITY TEST SUMMARY")
        print(f"{'=' * 60}")
        for name, status, message in results:
            print(f"{status} - {name}")
            if status != "✅ PASSED":
                print(f"  └─ {message}")
        
        return all_passed
    
    def test_analysis_history_retrieval(self) -> Tuple[bool, str]:
        """Test that analysis history endpoint works correctly"""
        try:
            response = self.session.get(f"{self.api_url}/analysis-history")
            if response.status_code != 200:
                return False, f"Analysis history endpoint failed with status {response.status_code}"
            
            data = response.json()
            if "history" not in data:
                return False, "Missing 'history' field in response"
            
            history_count = len(data["history"])
            print(f"Found {history_count} analysis entries in history")
            
            if history_count == 0:
                return False, "No analysis history found - cannot test backward compatibility"
            
            # Store analysis IDs for further testing
            self.analysis_ids = [entry["id"] for entry in data["history"]]
            print(f"Analysis IDs to test: {self.analysis_ids[:5]}...")  # Show first 5
            
            return True, f"Analysis history retrieved successfully with {history_count} entries"
            
        except Exception as e:
            return False, f"Analysis history retrieval failed: {str(e)}"
    
    def test_multiple_analysis_loading(self) -> Tuple[bool, str]:
        """Test loading multiple different analysis IDs from history"""
        if not hasattr(self, 'analysis_ids') or not self.analysis_ids:
            # Get analysis history first
            success, _ = self.test_analysis_history_retrieval()
            if not success:
                return False, "Could not retrieve analysis history for testing"
        
        successful_loads = 0
        failed_loads = 0
        error_details = []
        
        # Test up to 5 different analysis IDs
        test_ids = self.analysis_ids[:5]
        
        for analysis_id in test_ids:
            try:
                print(f"Testing analysis ID: {analysis_id}")
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify basic structure
                    if "market_input" in data and "market_map" in data:
                        successful_loads += 1
                        print(f"  ✅ Successfully loaded analysis {analysis_id}")
                    else:
                        failed_loads += 1
                        error_details.append(f"Analysis {analysis_id}: Missing required fields")
                        print(f"  ❌ Analysis {analysis_id}: Missing required fields")
                else:
                    failed_loads += 1
                    error_details.append(f"Analysis {analysis_id}: HTTP {response.status_code}")
                    print(f"  ❌ Analysis {analysis_id}: HTTP {response.status_code}")
                    
            except Exception as e:
                failed_loads += 1
                error_details.append(f"Analysis {analysis_id}: {str(e)}")
                print(f"  ❌ Analysis {analysis_id}: {str(e)}")
        
        if successful_loads == 0:
            return False, f"No analyses could be loaded. Errors: {'; '.join(error_details)}"
        elif failed_loads > 0:
            return False, f"Some analyses failed to load ({failed_loads}/{len(test_ids)}). Errors: {'; '.join(error_details)}"
        else:
            return True, f"All {successful_loads} analyses loaded successfully"
    
    def test_default_values(self) -> Tuple[bool, str]:
        """Test that older reports get default values for missing fields"""
        if not hasattr(self, 'analysis_ids') or not self.analysis_ids:
            success, _ = self.test_analysis_history_retrieval()
            if not success:
                return False, "Could not retrieve analysis history for testing"
        
        analyses_with_defaults = 0
        analyses_checked = 0
        field_issues = []
        
        # Test first 3 analysis IDs
        for analysis_id in self.analysis_ids[:3]:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                if response.status_code != 200:
                    continue
                
                data = response.json()
                analyses_checked += 1
                
                market_map = data.get("market_map", {})
                
                # Check for required fields with default values
                analysis_perspective = market_map.get("analysis_perspective")
                brand_position = market_map.get("brand_position")
                segmentation_by_firmographics = market_map.get("segmentation_by_firmographics")
                
                print(f"Analysis {analysis_id}:")
                print(f"  - analysis_perspective: {analysis_perspective}")
                print(f"  - brand_position: {brand_position}")
                print(f"  - segmentation_by_firmographics: {len(segmentation_by_firmographics) if segmentation_by_firmographics else 'None'}")
                
                # Verify default values are present
                has_valid_defaults = True
                
                if analysis_perspective is None:
                    field_issues.append(f"Analysis {analysis_id}: missing analysis_perspective")
                    has_valid_defaults = False
                elif analysis_perspective not in ["existing_brand", "new_entrant"]:
                    field_issues.append(f"Analysis {analysis_id}: invalid analysis_perspective value")
                    has_valid_defaults = False
                
                # brand_position can be None (for new_entrant) or a string (for existing_brand)
                if analysis_perspective == "existing_brand" and brand_position is None:
                    print(f"  Note: existing_brand with None brand_position - this may be expected for some cases")
                
                # segmentation_by_firmographics should be a list (can be empty)
                if segmentation_by_firmographics is None:
                    field_issues.append(f"Analysis {analysis_id}: segmentation_by_firmographics is None instead of empty list")
                    has_valid_defaults = False
                elif not isinstance(segmentation_by_firmographics, list):
                    field_issues.append(f"Analysis {analysis_id}: segmentation_by_firmographics is not a list")
                    has_valid_defaults = False
                
                if has_valid_defaults:
                    analyses_with_defaults += 1
                    
            except Exception as e:
                field_issues.append(f"Analysis {analysis_id}: Exception {str(e)}")
        
        if analyses_checked == 0:
            return False, "No analyses could be checked for default values"
        
        if analyses_with_defaults == analyses_checked:
            return True, f"All {analyses_checked} analyses have proper default values"
        else:
            return False, f"Only {analyses_with_defaults}/{analyses_checked} analyses have proper defaults. Issues: {'; '.join(field_issues)}"
    
    def test_visual_map_compatibility(self) -> Tuple[bool, str]:
        """Test that visual map generation works with both old and new data structures"""
        if not hasattr(self, 'analysis_ids') or not self.analysis_ids:
            success, _ = self.test_analysis_history_retrieval()
            if not success:
                return False, "Could not retrieve analysis history for testing"
        
        visual_maps_generated = 0
        visual_map_failures = []
        
        # Test first 3 analysis IDs
        for analysis_id in self.analysis_ids[:3]:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                if response.status_code != 200:
                    continue
                
                data = response.json()
                visual_map = data.get("visual_map")
                
                if visual_map is None:
                    visual_map_failures.append(f"Analysis {analysis_id}: No visual_map generated")
                    continue
                
                # Check visual map structure
                required_fields = [
                    "title", "geographic_segments", "demographic_segments", 
                    "psychographic_segments", "behavioral_segments", "firmographic_segments"
                ]
                
                missing_fields = []
                for field in required_fields:
                    if field not in visual_map:
                        missing_fields.append(field)
                
                if missing_fields:
                    visual_map_failures.append(f"Analysis {analysis_id}: Missing visual map fields: {missing_fields}")
                    continue
                
                # Check that firmographic_segments is handled properly (can be empty for B2C)
                firmographic_segments = visual_map.get("firmographic_segments", [])
                if not isinstance(firmographic_segments, list):
                    visual_map_failures.append(f"Analysis {analysis_id}: firmographic_segments is not a list")
                    continue
                
                visual_maps_generated += 1
                print(f"✅ Analysis {analysis_id}: Visual map generated successfully")
                print(f"  - Geographic segments: {len(visual_map.get('geographic_segments', []))}")
                print(f"  - Demographic segments: {len(visual_map.get('demographic_segments', []))}")
                print(f"  - Firmographic segments: {len(firmographic_segments)}")
                
            except Exception as e:
                visual_map_failures.append(f"Analysis {analysis_id}: Exception {str(e)}")
        
        if visual_maps_generated == 0:
            return False, f"No visual maps could be generated. Failures: {'; '.join(visual_map_failures)}"
        elif visual_map_failures:
            return False, f"Some visual maps failed ({len(visual_map_failures)} failures): {'; '.join(visual_map_failures)}"
        else:
            return True, f"All {visual_maps_generated} visual maps generated successfully"
    
    def test_mixed_analysis_retrieval(self) -> Tuple[bool, str]:
        """Test that both new and old analyses can be retrieved without errors"""
        if not hasattr(self, 'analysis_ids') or not self.analysis_ids:
            success, _ = self.test_analysis_history_retrieval()
            if not success:
                return False, "Could not retrieve analysis history for testing"
        
        # Create a new analysis to test mixed retrieval
        new_analysis_data = {
            "product_name": "Backward Compatibility Test Product",
            "industry": "Software Testing",
            "geography": "Global",
            "target_user": "QA Engineers",
            "demand_driver": "Quality assurance needs",
            "transaction_type": "Subscription",
            "key_metrics": "Test coverage, bug detection",
            "benchmarks": "Industry standard testing practices"
        }
        
        try:
            # Create new analysis
            response = self.session.post(f"{self.api_url}/analyze-market", json=new_analysis_data)
            if response.status_code != 200:
                return False, f"Failed to create new analysis for mixed testing: {response.status_code}"
            
            new_analysis = response.json()
            new_analysis_id = new_analysis["market_map"]["id"]
            print(f"Created new analysis for testing: {new_analysis_id}")
            
            # Test retrieving both old and new analyses
            test_ids = [new_analysis_id] + self.analysis_ids[:2]  # New + 2 old
            
            successful_retrievals = 0
            retrieval_errors = []
            
            for analysis_id in test_ids:
                try:
                    response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Verify structure
                        if "market_input" in data and "market_map" in data and "visual_map" in data:
                            successful_retrievals += 1
                            
                            # Check for backward compatibility fields
                            market_map = data["market_map"]
                            has_perspective = "analysis_perspective" in market_map
                            has_firmographics = "segmentation_by_firmographics" in market_map
                            
                            print(f"✅ Analysis {analysis_id}: Retrieved successfully")
                            print(f"  - Has analysis_perspective: {has_perspective}")
                            print(f"  - Has segmentation_by_firmographics: {has_firmographics}")
                        else:
                            retrieval_errors.append(f"Analysis {analysis_id}: Missing required structure")
                    else:
                        retrieval_errors.append(f"Analysis {analysis_id}: HTTP {response.status_code}")
                        
                except Exception as e:
                    retrieval_errors.append(f"Analysis {analysis_id}: {str(e)}")
            
            if successful_retrievals == len(test_ids):
                return True, f"All {successful_retrievals} mixed analyses retrieved successfully"
            else:
                return False, f"Mixed retrieval failed: {'; '.join(retrieval_errors)}"
                
        except Exception as e:
            return False, f"Mixed analysis retrieval test failed: {str(e)}"

if __name__ == "__main__":
    print("Starting Backward Compatibility Tests for Market Map Generator")
    print("Testing fix for older reports missing new fields...")
    
    tester = BackwardCompatibilityTester()
    success = tester.run_backward_compatibility_tests()
    
    if success:
        print("\n✅ All backward compatibility tests passed!")
        print("✅ Older reports can now be loaded successfully with default values")
        print("✅ Visual map generation works with both old and new data structures")
        sys.exit(0)
    else:
        print("\n❌ Some backward compatibility tests failed.")
        print("❌ The fix may not be working correctly for all scenarios.")
        sys.exit(1)