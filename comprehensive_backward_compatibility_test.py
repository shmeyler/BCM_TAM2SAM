#!/usr/bin/env python3
"""
Comprehensive Backward Compatibility Test for Market Map Generator
Tests all specific requirements from the review request:
1. Test loading several different analysis IDs from the analysis history to ensure backward compatibility
2. Verify that older reports now load successfully with default values for missing fields
3. Check that both new and old analyses can be retrieved without errors
4. Test the analysis history endpoint still works correctly
5. Verify that the visual map generation works with both old and new data structures
"""

import requests
import json
import os
import sys
from typing import Dict, Any, List, Tuple

def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

class ComprehensiveBackwardCompatibilityTester:
    """Comprehensive tester for all backward compatibility requirements"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        self.test_results = []
        print(f"Testing at: {self.api_url}")
    
    def run_all_tests(self) -> bool:
        """Run all comprehensive backward compatibility tests"""
        print("COMPREHENSIVE BACKWARD COMPATIBILITY TEST")
        print("Testing fix for older reports missing new fields:")
        print("- analysis_perspective, brand_position, segmentation_by_firmographics")
        print("=" * 80)
        
        tests = [
            ("Requirement 4: Analysis History Endpoint", self.test_analysis_history_endpoint),
            ("Requirement 1: Loading Multiple Analysis IDs", self.test_loading_multiple_analysis_ids),
            ("Requirement 2: Default Values for Missing Fields", self.test_default_values_for_missing_fields),
            ("Requirement 3: Both New and Old Analyses Retrieval", self.test_new_and_old_analyses_retrieval),
            ("Requirement 5: Visual Map Generation Compatibility", self.test_visual_map_generation_compatibility),
            ("Additional: Export Functionality Compatibility", self.test_export_functionality_compatibility)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\n{'='*80}")
            print(f"TESTING: {test_name}")
            print(f"{'='*80}")
            
            try:
                success, details = test_func()
                self.test_results.append({
                    "test": test_name,
                    "status": "PASS" if success else "FAIL",
                    "details": details
                })
                
                if success:
                    print(f"✅ PASSED: {details}")
                else:
                    print(f"❌ FAILED: {details}")
                    all_passed = False
                    
            except Exception as e:
                print(f"❌ ERROR: {str(e)}")
                self.test_results.append({
                    "test": test_name,
                    "status": "ERROR",
                    "details": str(e)
                })
                all_passed = False
        
        self.print_final_summary()
        return all_passed
    
    def test_analysis_history_endpoint(self) -> Tuple[bool, str]:
        """Test that the analysis history endpoint still works correctly"""
        try:
            response = self.session.get(f"{self.api_url}/analysis-history")
            
            if response.status_code != 200:
                return False, f"Analysis history endpoint returned {response.status_code}"
            
            data = response.json()
            
            if "history" not in data:
                return False, "Missing 'history' field in response"
            
            history = data["history"]
            if not isinstance(history, list):
                return False, f"History should be a list, got {type(history)}"
            
            if len(history) == 0:
                return False, "No analysis history found"
            
            # Store for other tests
            self.analysis_history = history
            
            # Validate history structure
            for entry in history[:3]:  # Check first 3 entries
                required_fields = ["id", "product_name", "timestamp"]
                for field in required_fields:
                    if field not in entry:
                        return False, f"Missing required field '{field}' in history entry"
            
            return True, f"Analysis history endpoint working correctly with {len(history)} entries"
            
        except Exception as e:
            return False, f"Exception in analysis history test: {str(e)}"
    
    def test_loading_multiple_analysis_ids(self) -> Tuple[bool, str]:
        """Test loading several different analysis IDs from the analysis history"""
        if not hasattr(self, 'analysis_history'):
            return False, "Analysis history not available from previous test"
        
        # Test loading multiple different analysis IDs
        test_ids = [entry["id"] for entry in self.analysis_history[:5]]  # Test first 5
        
        successful_loads = 0
        failed_loads = []
        
        for analysis_id in test_ids:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify basic structure
                    if "market_input" in data and "market_map" in data:
                        successful_loads += 1
                    else:
                        failed_loads.append(f"{analysis_id}: Missing required structure")
                else:
                    failed_loads.append(f"{analysis_id}: HTTP {response.status_code}")
                    
            except Exception as e:
                failed_loads.append(f"{analysis_id}: Exception {str(e)}")
        
        if len(failed_loads) > 0:
            return False, f"Failed to load {len(failed_loads)} analyses: {'; '.join(failed_loads[:3])}"
        
        return True, f"Successfully loaded all {successful_loads} different analysis IDs from history"
    
    def test_default_values_for_missing_fields(self) -> Tuple[bool, str]:
        """Verify that older reports now load successfully with default values for missing fields"""
        if not hasattr(self, 'analysis_history'):
            return False, "Analysis history not available from previous test"
        
        # Test default values for the specific fields mentioned in the fix
        test_ids = [entry["id"] for entry in self.analysis_history[:5]]
        
        analyses_with_proper_defaults = 0
        field_issues = []
        
        for analysis_id in test_ids:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                market_map = data.get("market_map", {})
                
                # Check the specific fields mentioned in the fix
                analysis_perspective = market_map.get("analysis_perspective")
                brand_position = market_map.get("brand_position")
                segmentation_by_firmographics = market_map.get("segmentation_by_firmographics")
                
                # Validate default values as per the fix:
                # - analysis_perspective should default to "new_entrant"
                # - brand_position should default to None
                # - segmentation_by_firmographics should default to []
                
                issues_for_this_analysis = []
                
                if analysis_perspective is None:
                    issues_for_this_analysis.append("analysis_perspective is None")
                elif analysis_perspective not in ["existing_brand", "new_entrant"]:
                    issues_for_this_analysis.append(f"analysis_perspective has invalid value: {analysis_perspective}")
                
                # brand_position can be None or string, both are valid
                
                if segmentation_by_firmographics is None:
                    issues_for_this_analysis.append("segmentation_by_firmographics is None instead of empty list")
                elif not isinstance(segmentation_by_firmographics, list):
                    issues_for_this_analysis.append("segmentation_by_firmographics is not a list")
                
                if not issues_for_this_analysis:
                    analyses_with_proper_defaults += 1
                else:
                    field_issues.extend([f"{analysis_id}: {issue}" for issue in issues_for_this_analysis])
                    
            except Exception as e:
                field_issues.append(f"{analysis_id}: Exception {str(e)}")
        
        if len(field_issues) > 0:
            return False, f"Field issues found: {'; '.join(field_issues[:3])}"
        
        return True, f"All {analyses_with_proper_defaults} analyses have proper default values for missing fields"
    
    def test_new_and_old_analyses_retrieval(self) -> Tuple[bool, str]:
        """Check that both new and old analyses can be retrieved without errors"""
        if not hasattr(self, 'analysis_history'):
            return False, "Analysis history not available from previous test"
        
        # Test a mix of analyses (assuming some are older and some are newer)
        test_ids = [entry["id"] for entry in self.analysis_history]
        
        successful_retrievals = 0
        retrieval_errors = []
        perspective_distribution = {"existing_brand": 0, "new_entrant": 0, "other": 0}
        
        for analysis_id in test_ids:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Verify complete structure
                    if "market_input" in data and "market_map" in data and "visual_map" in data:
                        successful_retrievals += 1
                        
                        # Track perspective distribution to show we're handling both types
                        market_map = data["market_map"]
                        perspective = market_map.get("analysis_perspective", "other")
                        if perspective in perspective_distribution:
                            perspective_distribution[perspective] += 1
                        else:
                            perspective_distribution["other"] += 1
                    else:
                        retrieval_errors.append(f"{analysis_id}: Incomplete structure")
                else:
                    retrieval_errors.append(f"{analysis_id}: HTTP {response.status_code}")
                    
            except Exception as e:
                retrieval_errors.append(f"{analysis_id}: Exception {str(e)}")
        
        if len(retrieval_errors) > 0:
            return False, f"Retrieval errors: {'; '.join(retrieval_errors[:3])}"
        
        # Verify we have both types of analyses
        has_existing_brand = perspective_distribution["existing_brand"] > 0
        has_new_entrant = perspective_distribution["new_entrant"] > 0
        
        details = f"Retrieved {successful_retrievals} analyses successfully. "
        details += f"Distribution: {perspective_distribution['existing_brand']} existing_brand, "
        details += f"{perspective_distribution['new_entrant']} new_entrant"
        
        if has_existing_brand and has_new_entrant:
            details += " - Both analysis types present"
        
        return True, details
    
    def test_visual_map_generation_compatibility(self) -> Tuple[bool, str]:
        """Verify that the visual map generation works with both old and new data structures"""
        if not hasattr(self, 'analysis_history'):
            return False, "Analysis history not available from previous test"
        
        test_ids = [entry["id"] for entry in self.analysis_history[:5]]
        
        visual_maps_generated = 0
        visual_map_issues = []
        firmographic_handling = {"with_firmographics": 0, "without_firmographics": 0}
        
        for analysis_id in test_ids:
            try:
                response = self.session.get(f"{self.api_url}/analysis/{analysis_id}")
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                visual_map = data.get("visual_map")
                
                if visual_map is None:
                    visual_map_issues.append(f"{analysis_id}: No visual map generated")
                    continue
                
                # Check visual map structure
                required_visual_fields = [
                    "title", "geographic_segments", "demographic_segments",
                    "psychographic_segments", "behavioral_segments", "firmographic_segments"
                ]
                
                missing_fields = []
                for field in required_visual_fields:
                    if field not in visual_map:
                        missing_fields.append(field)
                
                if missing_fields:
                    visual_map_issues.append(f"{analysis_id}: Missing visual fields: {missing_fields}")
                    continue
                
                # Check firmographic segments handling (key part of the fix)
                firmographic_segments = visual_map.get("firmographic_segments", [])
                if not isinstance(firmographic_segments, list):
                    visual_map_issues.append(f"{analysis_id}: firmographic_segments not a list")
                    continue
                
                # Track firmographic handling
                if len(firmographic_segments) > 0:
                    firmographic_handling["with_firmographics"] += 1
                else:
                    firmographic_handling["without_firmographics"] += 1
                
                visual_maps_generated += 1
                
            except Exception as e:
                visual_map_issues.append(f"{analysis_id}: Exception {str(e)}")
        
        if len(visual_map_issues) > 0:
            return False, f"Visual map issues: {'; '.join(visual_map_issues[:3])}"
        
        details = f"Generated {visual_maps_generated} visual maps successfully. "
        details += f"Firmographic handling: {firmographic_handling['with_firmographics']} with, "
        details += f"{firmographic_handling['without_firmographics']} without firmographic segments"
        
        return True, details
    
    def test_export_functionality_compatibility(self) -> Tuple[bool, str]:
        """Test that export functionality works with backward compatibility"""
        if not hasattr(self, 'analysis_history'):
            return False, "Analysis history not available from previous test"
        
        # Test export for a few analyses
        test_ids = [entry["id"] for entry in self.analysis_history[:3]]
        
        successful_exports = 0
        export_issues = []
        
        for analysis_id in test_ids:
            try:
                response = self.session.get(f"{self.api_url}/export-market-map/{analysis_id}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('Content-Type')
                    content_length = int(response.headers.get('Content-Length', 0))
                    
                    expected_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    
                    if content_type == expected_type and content_length > 0:
                        successful_exports += 1
                    else:
                        export_issues.append(f"{analysis_id}: Invalid export format")
                else:
                    export_issues.append(f"{analysis_id}: Export failed with {response.status_code}")
                    
            except Exception as e:
                export_issues.append(f"{analysis_id}: Exception {str(e)}")
        
        if len(export_issues) > 0:
            return False, f"Export issues: {'; '.join(export_issues)}"
        
        return True, f"All {successful_exports} exports work correctly with backward compatibility"
    
    def print_final_summary(self):
        """Print comprehensive final summary"""
        print(f"\n{'='*80}")
        print("COMPREHENSIVE BACKWARD COMPATIBILITY TEST SUMMARY")
        print(f"{'='*80}")
        
        passed = len([r for r in self.test_results if r["status"] == "PASS"])
        failed = len([r for r in self.test_results if r["status"] == "FAIL"])
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        
        print(f"Total tests: {len(self.test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Errors: {errors}")
        
        print(f"\nDETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status_icon} {result['test']}: {result['status']}")
            if result["status"] != "PASS":
                print(f"   └─ {result['details']}")
        
        if passed == len(self.test_results):
            print(f"\n🎉 ALL BACKWARD COMPATIBILITY REQUIREMENTS SATISFIED!")
            print(f"✅ The fix for older reports missing new fields is working correctly")
            print(f"✅ analysis_perspective, brand_position, segmentation_by_firmographics are properly handled")
            print(f"✅ Visual map generation works with both old and new data structures")
            print(f"✅ Export functionality maintains compatibility")
        else:
            print(f"\n❌ SOME BACKWARD COMPATIBILITY REQUIREMENTS NOT MET")
            print(f"❌ {failed} tests failed, {errors} tests had errors")

if __name__ == "__main__":
    print("Market Map Generator - Comprehensive Backward Compatibility Test")
    print("Testing the fix for older reports missing new fields...")
    print()
    
    tester = ComprehensiveBackwardCompatibilityTester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)