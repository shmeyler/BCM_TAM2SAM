#!/usr/bin/env python3
"""
Focused Test for Market Map Generator Text Spacing and Perspective Analysis Fixes
This script specifically tests the two fixes mentioned in the review request:
1. Text spacing issues (like "Platformacross")
2. Perspective analysis (existing_brand vs new_entrant)
"""

import requests
import json
import os
import sys
import time
import re
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

class SpacingPerspectiveAPITester:
    """Class to test specific fixes for text spacing and perspective analysis"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
    def check_text_spacing(self, text: str) -> List[str]:
        """Check for spacing issues in text and return list of problems found"""
        issues = []
        
        # Check for common spacing issues
        # 1. Missing spaces between words (like "Platformacross")
        # Pattern: lowercase letter followed by uppercase letter without space
        missing_spaces = re.findall(r'[a-z][A-Z]', text)
        if missing_spaces:
            issues.append(f"Missing spaces between words: {missing_spaces}")
        
        # 2. Missing spaces around company names or product names
        # Pattern: word+word without space
        word_concatenation = re.findall(r'[a-zA-Z]+[A-Z][a-z]+[a-zA-Z]+', text)
        suspicious_concatenations = [w for w in word_concatenation if len(w) > 10]
        if suspicious_concatenations:
            issues.append(f"Suspicious word concatenations: {suspicious_concatenations}")
        
        # 3. Missing spaces before/after numbers
        number_spacing = re.findall(r'[a-zA-Z]\d|\d[a-zA-Z]', text)
        if number_spacing:
            issues.append(f"Missing spaces around numbers: {number_spacing}")
        
        # 4. Double spaces or extra whitespace
        extra_spaces = re.findall(r'\s{2,}', text)
        if extra_spaces:
            issues.append(f"Extra whitespace found: {len(extra_spaces)} instances")
        
        return issues
    
    def analyze_text_in_response(self, data: Dict[str, Any]) -> List[str]:
        """Analyze all text fields in the API response for spacing issues"""
        all_issues = []
        
        # Check executive summary
        if 'market_map' in data and 'executive_summary' in data['market_map']:
            summary_issues = self.check_text_spacing(data['market_map']['executive_summary'])
            if summary_issues:
                all_issues.extend([f"Executive Summary: {issue}" for issue in summary_issues])
        
        # Check competitor descriptions
        if 'market_map' in data and 'competitors' in data['market_map']:
            for i, comp in enumerate(data['market_map']['competitors']):
                comp_name = comp.get('name', '')
                comp_issues = self.check_text_spacing(comp_name)
                if comp_issues:
                    all_issues.extend([f"Competitor {i+1} name: {issue}" for issue in comp_issues])
                
                # Check strengths and weaknesses
                for strength in comp.get('strengths', []):
                    strength_issues = self.check_text_spacing(strength)
                    if strength_issues:
                        all_issues.extend([f"Competitor {i+1} strength: {issue}" for issue in strength_issues])
                
                for weakness in comp.get('weaknesses', []):
                    weakness_issues = self.check_text_spacing(weakness)
                    if weakness_issues:
                        all_issues.extend([f"Competitor {i+1} weakness: {issue}" for issue in weakness_issues])
        
        # Check segmentation descriptions
        segmentation_types = ['segmentation_by_geographics', 'segmentation_by_demographics', 
                             'segmentation_by_psychographics', 'segmentation_by_behavioral']
        
        if 'market_map' in data:
            for seg_type in segmentation_types:
                if seg_type in data['market_map']:
                    for i, segment in enumerate(data['market_map'][seg_type]):
                        seg_desc = segment.get('description', '')
                        seg_issues = self.check_text_spacing(seg_desc)
                        if seg_issues:
                            all_issues.extend([f"{seg_type} segment {i+1}: {issue}" for issue in seg_issues])
        
        return all_issues
    
    def test_text_spacing_fix(self) -> Tuple[bool, str]:
        """Test various scenarios to ensure no spacing issues like 'Platformacross'"""
        print("Testing text spacing fixes...")
        
        # Test scenarios with different product names and industries
        test_scenarios = [
            {
                "product_name": "Platform Solutions",
                "industry": "Software Technology",
                "geography": "North America",
                "target_user": "Enterprise customers",
                "demand_driver": "Digital transformation across industries",
                "transaction_type": "Subscription",
                "key_metrics": "Platform adoption rates",
                "benchmarks": "Growing market segment"
            },
            {
                "product_name": "CRM Software Platform",
                "industry": "SaaS Software",
                "geography": "Global",
                "target_user": "Business professionals",
                "demand_driver": "Remote work trends",
                "transaction_type": "Monthly subscription",
                "key_metrics": "User engagement metrics",
                "benchmarks": "Competitive landscape analysis"
            },
            {
                "product_name": "Analytics Dashboard",
                "industry": "Business Intelligence",
                "geography": "United States",
                "target_user": "Data analysts",
                "demand_driver": "Data-driven decision making",
                "transaction_type": "Annual license",
                "key_metrics": "Dashboard usage statistics",
                "benchmarks": "Industry standard metrics"
            }
        ]
        
        all_spacing_issues = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"\nTesting scenario {i+1}: {scenario['product_name']}")
            
            try:
                response = self.session.post(
                    f"{self.api_url}/analyze-market",
                    json=scenario
                )
                
                if response.status_code != 200:
                    return False, f"API call failed for scenario {i+1}: {response.status_code}"
                
                data = response.json()
                
                # Analyze text spacing in the response
                spacing_issues = self.analyze_text_in_response(data)
                if spacing_issues:
                    all_spacing_issues.extend([f"Scenario {i+1} ({scenario['product_name']}): {issue}" for issue in spacing_issues])
                    print(f"  ❌ Found spacing issues: {len(spacing_issues)}")
                    for issue in spacing_issues[:3]:  # Show first 3 issues
                        print(f"    - {issue}")
                else:
                    print(f"  ✅ No spacing issues found")
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                return False, f"Error testing scenario {i+1}: {str(e)}"
        
        if all_spacing_issues:
            return False, f"Found {len(all_spacing_issues)} text spacing issues across all scenarios"
        else:
            return True, "All text spacing tests passed - no spacing issues found"
    
    def test_perspective_analysis(self) -> Tuple[bool, str]:
        """Test existing brand vs new entrant perspective analysis"""
        print("Testing perspective analysis...")
        
        # Test scenarios for existing brand analysis
        existing_brand_scenarios = [
            {
                "product_name": "Salesforce CRM",
                "industry": "SaaS Software",
                "geography": "Global",
                "target_user": "Sales teams",
                "demand_driver": "Sales automation needs",
                "transaction_type": "Subscription",
                "key_metrics": "User adoption",
                "benchmarks": "Market leader",
                "expected_perspective": "existing_brand"
            },
            {
                "product_name": "Apple iPhone",
                "industry": "Consumer Electronics",
                "geography": "Global",
                "target_user": "Smartphone users",
                "demand_driver": "Mobile technology advancement",
                "transaction_type": "One-time purchase",
                "key_metrics": "Device sales",
                "benchmarks": "Premium segment leader",
                "expected_perspective": "existing_brand"
            }
        ]
        
        # Test scenarios for new entrant analysis
        new_entrant_scenarios = [
            {
                "product_name": "New CRM Tool",
                "industry": "SaaS Software",
                "geography": "North America",
                "target_user": "Small businesses",
                "demand_driver": "Affordable CRM solutions",
                "transaction_type": "Monthly subscription",
                "key_metrics": "Customer acquisition",
                "benchmarks": "Emerging market segment",
                "expected_perspective": "new_entrant"
            },
            {
                "product_name": "Startup Analytics Platform",
                "industry": "Business Intelligence",
                "geography": "United States",
                "target_user": "Startups and SMBs",
                "demand_driver": "Accessible analytics tools",
                "transaction_type": "Freemium model",
                "key_metrics": "Platform usage",
                "benchmarks": "New market entrant",
                "expected_perspective": "new_entrant"
            }
        ]
        
        all_scenarios = existing_brand_scenarios + new_entrant_scenarios
        perspective_issues = []
        
        for i, scenario in enumerate(all_scenarios):
            print(f"\nTesting perspective scenario {i+1}: {scenario['product_name']}")
            expected = scenario.pop('expected_perspective')
            
            try:
                response = self.session.post(
                    f"{self.api_url}/analyze-market",
                    json=scenario
                )
                
                if response.status_code != 200:
                    return False, f"API call failed for perspective scenario {i+1}: {response.status_code}"
                
                data = response.json()
                
                # Check analysis_perspective field
                actual_perspective = data.get('market_map', {}).get('analysis_perspective')
                
                if actual_perspective != expected:
                    issue = f"Scenario {i+1} ({scenario['product_name']}): Expected '{expected}', got '{actual_perspective}'"
                    perspective_issues.append(issue)
                    print(f"  ❌ {issue}")
                else:
                    print(f"  ✅ Correct perspective: {actual_perspective}")
                
                # For existing brands, check if brand_position field exists
                if expected == "existing_brand":
                    brand_position = data.get('market_map', {}).get('brand_position')
                    if not brand_position:
                        issue = f"Scenario {i+1} ({scenario['product_name']}): Missing brand_position field for existing brand"
                        perspective_issues.append(issue)
                        print(f"  ❌ {issue}")
                    else:
                        print(f"  ✅ Brand position provided: {brand_position[:50]}...")
                
                # For new entrants, brand_position should be None or not present
                elif expected == "new_entrant":
                    brand_position = data.get('market_map', {}).get('brand_position')
                    if brand_position:
                        issue = f"Scenario {i+1} ({scenario['product_name']}): Unexpected brand_position field for new entrant: {brand_position}"
                        perspective_issues.append(issue)
                        print(f"  ❌ {issue}")
                    else:
                        print(f"  ✅ No brand position for new entrant (correct)")
                
                # Small delay between requests
                time.sleep(1)
                
            except Exception as e:
                return False, f"Error testing perspective scenario {i+1}: {str(e)}"
        
        if perspective_issues:
            return False, f"Found {len(perspective_issues)} perspective analysis issues"
        else:
            return True, "All perspective analysis tests passed"
    
    def test_api_response_validation(self) -> Tuple[bool, str]:
        """Test that API responses have proper structure and formatting"""
        print("Testing API response validation...")
        
        test_data = {
            "product_name": "Test Product Platform",
            "industry": "Technology Software",
            "geography": "Global Market",
            "target_user": "Business users",
            "demand_driver": "Digital transformation",
            "transaction_type": "Subscription model",
            "key_metrics": "User engagement",
            "benchmarks": "Industry standards"
        }
        
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=test_data
            )
            
            if response.status_code != 200:
                return False, f"API call failed: {response.status_code}"
            
            data = response.json()
            validation_issues = []
            
            # Check required fields
            required_fields = ['market_input', 'market_map', 'visual_map']
            for field in required_fields:
                if field not in data:
                    validation_issues.append(f"Missing required field: {field}")
            
            # Check market_map structure
            if 'market_map' in data:
                market_map = data['market_map']
                required_market_map_fields = [
                    'analysis_perspective', 'total_market_size', 'market_growth_rate',
                    'competitors', 'executive_summary'
                ]
                for field in required_market_map_fields:
                    if field not in market_map:
                        validation_issues.append(f"Missing market_map field: {field}")
            
            # Check that competitors list is not empty and has minimum count
            if 'market_map' in data and 'competitors' in data['market_map']:
                competitors = data['market_map']['competitors']
                if len(competitors) < 3:
                    validation_issues.append(f"Insufficient competitors: {len(competitors)} (minimum 3 expected)")
            
            # Check that executive summary is substantial
            if 'market_map' in data and 'executive_summary' in data['market_map']:
                summary = data['market_map']['executive_summary']
                if len(summary) < 200:
                    validation_issues.append(f"Executive summary too short: {len(summary)} characters")
            
            if validation_issues:
                return False, f"API response validation failed: {'; '.join(validation_issues)}"
            else:
                return True, "API response validation passed"
                
        except Exception as e:
            return False, f"API response validation failed: {str(e)}"
    
    def run_focused_tests(self) -> bool:
        """Run the focused tests for the specific fixes"""
        tests = [
            ("Text Spacing Fix", self.test_text_spacing_fix),
            ("Perspective Analysis", self.test_perspective_analysis),
            ("API Response Validation", self.test_api_response_validation)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"Running Focused Test: {test_name}")
            print(f"{'=' * 60}")
            
            try:
                success, message = test_func()
                status = "✅ PASSED" if success else "❌ FAILED"
                results.append((test_name, status, message))
                if not success:
                    all_passed = False
                print(f"\nResult: {status} - {message}")
            except Exception as e:
                results.append((test_name, "❌ ERROR", str(e)))
                all_passed = False
                print(f"Error during test: {e}")
        
        # Print summary
        print("\n\n")
        print(f"{'=' * 60}")
        print("FOCUSED TEST SUMMARY")
        print(f"{'=' * 60}")
        for name, status, message in results:
            print(f"{status} - {name}")
            if status != "✅ PASSED":
                print(f"  └─ {message}")
        
        return all_passed


if __name__ == "__main__":
    print("Starting Focused Tests for Text Spacing and Perspective Analysis Fixes")
    tester = SpacingPerspectiveAPITester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n✅ All focused tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some focused tests failed. See details above.")
        sys.exit(1)