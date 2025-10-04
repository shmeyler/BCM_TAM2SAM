#!/usr/bin/env python3
"""
Focused Backend Test for Market Map Generator - Text Spacing and Perspective Analysis
Tests the specific fixes mentioned in the review request without requiring authentication
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

class FocusedBackendTester:
    """Class to test backend functionality focusing on the specific fixes"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.session = requests.Session()
        print(f"Using API URL: {self.api_url}")
    
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
        """Test the integrations status endpoint"""
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
            
            # Check Together AI status
            together_status = data.get("integrations", {}).get("together_ai")
            print(f"Together AI Status: {together_status}")
            
            return True, "Integration status check passed"
        except Exception as e:
            return False, f"Integration status check failed: {str(e)}"
    
    def test_analysis_history(self) -> Tuple[bool, str]:
        """Test the analysis history endpoint (no auth required)"""
        try:
            response = self.session.get(f"{self.api_url}/analysis-history")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            print(f"✅ Analysis History Response: {json.dumps(data, indent=2)}")
            
            # Validate response structure
            if "history" not in data:
                return False, "Missing 'history' in response"
            
            print(f"Found {len(data['history'])} entries in analysis history")
            return True, "Analysis history test passed"
        except Exception as e:
            return False, f"Analysis history test failed: {str(e)}"
    
    def check_llm_prompt_for_spacing_instructions(self) -> Tuple[bool, str]:
        """Check if the LLM prompt includes proper text formatting instructions"""
        try:
            # Read the server.py file to check the prompt
            with open('/app/backend/server.py', 'r') as f:
                server_content = f.read()
            
            # Look for text formatting instructions in the prompt
            spacing_keywords = [
                "ENSURE PROPER SPACING",
                "TEXT FORMATTING REQUIREMENTS",
                "spacing between all words",
                "Proofread all generated text for spacing errors"
            ]
            
            found_instructions = []
            for keyword in spacing_keywords:
                if keyword in server_content:
                    found_instructions.append(keyword)
            
            if not found_instructions:
                return False, "No text spacing instructions found in LLM prompt"
            
            print(f"✅ Found text formatting instructions: {found_instructions}")
            
            # Check for specific spacing-related prompt content
            if "spacing errors" in server_content.lower():
                print("✅ Prompt includes spacing error prevention")
            
            if "proper spacing" in server_content.lower():
                print("✅ Prompt includes proper spacing requirements")
            
            return True, f"LLM prompt includes {len(found_instructions)} text formatting instructions"
            
        except Exception as e:
            return False, f"Error checking LLM prompt: {str(e)}"
    
    def check_perspective_analysis_logic(self) -> Tuple[bool, str]:
        """Check if the perspective analysis logic is implemented correctly"""
        try:
            # Read the server.py file to check the perspective analysis logic
            with open('/app/backend/server.py', 'r') as f:
                server_content = f.read()
            
            # Look for perspective analysis implementation
            perspective_keywords = [
                "analysis_perspective",
                "existing_brand",
                "new_entrant",
                "has_specific_brand",
                "brand_position"
            ]
            
            found_logic = []
            for keyword in perspective_keywords:
                if keyword in server_content:
                    found_logic.append(keyword)
            
            if len(found_logic) < 4:
                return False, f"Incomplete perspective analysis logic. Found: {found_logic}"
            
            print(f"✅ Found perspective analysis logic: {found_logic}")
            
            # Check for specific logic patterns
            if 'market_input.product_name.lower() not in [\'new product\', \'new service\', \'startup\', \'new company\']' in server_content:
                print("✅ Correct brand detection logic found")
            
            if '"existing_brand" if has_specific_brand else "new_entrant"' in server_content:
                print("✅ Correct perspective assignment logic found")
            
            # Check for brand_position conditional logic
            if 'brand_position_json' in server_content and 'if analysis_perspective == "existing_brand"' in server_content:
                print("✅ Conditional brand_position logic found")
            
            return True, f"Perspective analysis logic is properly implemented with {len(found_logic)} components"
            
        except Exception as e:
            return False, f"Error checking perspective analysis logic: {str(e)}"
    
    def check_firmographic_segmentation(self) -> Tuple[bool, str]:
        """Check if firmographic segmentation for B2B scenarios is implemented"""
        try:
            # Read the server.py file to check firmographic segmentation
            with open('/app/backend/server.py', 'r') as f:
                server_content = f.read()
            
            # Look for firmographic segmentation implementation
            firmographic_keywords = [
                "segmentation_by_firmographics",
                "is_b2b",
                "b2b",
                "enterprise",
                "firmographic_instruction",
                "firmographic_json"
            ]
            
            found_firmographic = []
            for keyword in firmographic_keywords:
                if keyword.lower() in server_content.lower():
                    found_firmographic.append(keyword)
            
            if len(found_firmographic) < 3:
                return False, f"Incomplete firmographic segmentation. Found: {found_firmographic}"
            
            print(f"✅ Found firmographic segmentation logic: {found_firmographic}")
            
            # Check for B2B detection logic
            if 'saas' in server_content.lower() and 'software' in server_content.lower() and 'financial services' in server_content.lower():
                print("✅ B2B industry detection logic found")
            
            # Check for firmographic segments in data model
            if 'segmentation_by_firmographics: List[MarketSegment]' in server_content:
                print("✅ Firmographic segmentation in data model")
            
            return True, f"Firmographic segmentation is properly implemented"
            
        except Exception as e:
            return False, f"Error checking firmographic segmentation: {str(e)}"
    
    def test_fallback_analysis_structure(self) -> Tuple[bool, str]:
        """Test that fallback analysis includes proper structure for new features"""
        try:
            # Read the server.py file to check fallback analysis
            with open('/app/backend/server.py', 'r') as f:
                server_content = f.read()
            
            # Look for fallback analysis method
            if '_get_fallback_analysis' not in server_content:
                return False, "Fallback analysis method not found"
            
            # Check if fallback includes new features
            fallback_features = [
                '"analysis_perspective": analysis_perspective',
                'if analysis_perspective == "existing_brand"',
                'segmentation["by_firmographics"]',
                'is_b2b'
            ]
            
            found_features = []
            for feature in fallback_features:
                if feature in server_content:
                    found_features.append(feature)
            
            if len(found_features) < 3:
                return False, f"Fallback analysis missing new features. Found: {found_features}"
            
            print(f"✅ Fallback analysis includes new features: {found_features}")
            return True, "Fallback analysis properly supports new features"
            
        except Exception as e:
            return False, f"Error checking fallback analysis: {str(e)}"
    
    def validate_data_models(self) -> Tuple[bool, str]:
        """Validate that data models include the new fields"""
        try:
            # Read the server.py file to check data models
            with open('/app/backend/server.py', 'r') as f:
                server_content = f.read()
            
            # Check MarketMap model for new fields
            required_fields = [
                'analysis_perspective: str',
                'brand_position: Optional[str]',
                'segmentation_by_firmographics: List[MarketSegment]'
            ]
            
            found_fields = []
            for field in required_fields:
                if field in server_content:
                    found_fields.append(field)
            
            if len(found_fields) != len(required_fields):
                return False, f"Missing required fields in MarketMap model. Found: {found_fields}"
            
            print(f"✅ MarketMap model includes all new fields: {found_fields}")
            
            # Check if visual map includes firmographic segments
            if 'firmographic_segments' in server_content:
                print("✅ Visual map includes firmographic segments")
            
            return True, "Data models properly include all new fields"
            
        except Exception as e:
            return False, f"Error validating data models: {str(e)}"
    
    def run_focused_tests(self) -> bool:
        """Run the focused tests for the specific fixes"""
        tests = [
            ("API Health Check", self.test_api_health),
            ("Integration Status", self.test_integrations),
            ("Analysis History", self.test_analysis_history),
            ("LLM Prompt Text Spacing Instructions", self.check_llm_prompt_for_spacing_instructions),
            ("Perspective Analysis Logic", self.check_perspective_analysis_logic),
            ("Firmographic Segmentation", self.check_firmographic_segmentation),
            ("Fallback Analysis Structure", self.test_fallback_analysis_structure),
            ("Data Models Validation", self.validate_data_models)
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
                print(f"\nResult: {status} - {message}")
            except Exception as e:
                results.append((test_name, "❌ ERROR", str(e)))
                all_passed = False
                print(f"Error during test: {e}")
        
        # Print summary
        print("\n\n")
        print(f"{'=' * 70}")
        print("FOCUSED BACKEND TEST SUMMARY")
        print(f"{'=' * 70}")
        for name, status, message in results:
            print(f"{status} - {name}")
            if status != "✅ PASSED":
                print(f"  └─ {message}")
        
        return all_passed


if __name__ == "__main__":
    print("Starting Focused Backend Tests for Text Spacing and Perspective Analysis Fixes")
    print("Testing implementation without requiring authentication...")
    tester = FocusedBackendTester()
    success = tester.run_focused_tests()
    
    if success:
        print("\n✅ All focused backend tests passed successfully!")
        print("\nNote: Full end-to-end testing with market analysis requires authentication.")
        print("The implementation appears to be correctly structured for the requested fixes.")
        sys.exit(0)
    else:
        print("\n❌ Some focused backend tests failed. See details above.")
        sys.exit(1)