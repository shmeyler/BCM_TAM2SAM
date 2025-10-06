#!/usr/bin/env python3
"""
Market Map Generator Backend API Test Script with Authentication
This script tests the functionality of the Market Map Generator backend API endpoints.
"""

import requests
import json
import os
import sys
import time
import uuid
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timezone, timedelta

# Get the backend URL from the frontend/.env file
def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

# Sample market data for testing
SAMPLE_MARKET_DATA = {
    "product_name": "Fitness Tracker",
    "industry": "Wearable Technology", 
    "geography": "Global",
    "target_user": "Health-conscious consumers",
    "demand_driver": "Health and wellness trends",
    "transaction_type": "One-time Purchase",
    "key_metrics": "Device sales, user engagement",
    "benchmarks": "Market growing at 9.2% CAGR"
}

class MarketMapAPITesterWithAuth:
    """Class to test the Market Map Generator API endpoints with authentication"""
    
    def __init__(self):
        self.base_url = get_backend_url()
        self.api_url = f"{self.base_url}/api"
        self.analysis_id = None
        self.session = requests.Session()
        self.auth_token = None
        print(f"Using API URL: {self.api_url}")
    
    def create_test_session(self) -> bool:
        """Create a test session by directly inserting into database"""
        try:
            import asyncio
            from motor.motor_asyncio import AsyncIOMotorClient
            from datetime import datetime, timezone, timedelta
            
            async def create_session():
                mongo_url = 'mongodb://localhost:27017'
                client = AsyncIOMotorClient(mongo_url)
                db = client['market_map_db']
                
                # Get an existing user
                user = await db.users.find_one({"is_active": True})
                if not user:
                    print("No active users found")
                    return None
                
                # Create a test session
                session_token = str(uuid.uuid4())
                session_data = {
                    "user_id": user["id"],
                    "session_token": session_token,
                    "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
                    "created_at": datetime.now(timezone.utc)
                }
                
                await db.sessions.insert_one(session_data)
                client.close()
                return session_token
            
            token = asyncio.run(create_session())
            if token:
                self.auth_token = token
                self.session.headers.update({"Authorization": f"Bearer {token}"})
                print(f"Created test session with token: {token[:20]}...")
                return True
            return False
            
        except Exception as e:
            print(f"Failed to create test session: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all API tests and return overall success status"""
        # Create test session for authenticated endpoints
        if not self.create_test_session():
            print("Warning: Could not create test session, authenticated endpoints will fail")
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("Integration Status", self.test_integrations),
            ("Market Analysis", self.test_analyze_market),
            ("Analysis History", self.test_analysis_history),
            ("Export Market Map", self.test_export_market_map)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 50}")
            print(f"Running Test: {test_name}")
            print(f"{'=' * 50}")
            
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
        print(f"{'=' * 50}")
        print("TEST SUMMARY")
        print(f"{'=' * 50}")
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
            
            print(f"API Health Response: {data}")
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
            print(f"Integration Status Response: {data}")
            
            # Check MongoDB status
            mongodb_status = data.get("integrations", {}).get("mongodb")
            if mongodb_status != "OK":
                return False, f"MongoDB integration failed: {mongodb_status}"
            
            # Check Together AI status
            together_status = data.get("integrations", {}).get("together_ai")
            if together_status == "OK":
                print("✅ Together AI integration is working")
            else:
                print(f"⚠️ Together AI status: {together_status}")
            
            return True, "Integration status check passed"
        except Exception as e:
            return False, f"Integration status check failed: {str(e)}"
    
    def test_analyze_market(self) -> Tuple[bool, str]:
        """Test the market analysis endpoint"""
        try:
            response = self.session.post(
                f"{self.api_url}/analyze-market",
                json=SAMPLE_MARKET_DATA
            )
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}. Response: {response.text[:200]}"
            
            data = response.json()
            print(f"Market Analysis Response (partial): {json.dumps(data, indent=2, default=str)[:500]}...")
            
            # Validate response structure
            if "market_input" not in data:
                return False, "Missing 'market_input' in response"
            if "market_map" not in data:
                return False, "Missing 'market_map' in response"
            if "visual_map" not in data:
                return False, "Missing 'visual_map' in response"
            
            # Check if the product name matches
            if data["market_input"]["product_name"] != SAMPLE_MARKET_DATA["product_name"]:
                return False, f"Product name mismatch: {data['market_input']['product_name']} vs {SAMPLE_MARKET_DATA['product_name']}"
            
            # Check for competitors (should include Apple, Fitbit, Garmin for fitness tracker)
            competitors = [comp["name"] for comp in data["market_map"]["competitors"]]
            expected_competitors = ["Apple", "Fitbit", "Garmin"]
            found_competitors = [comp for comp in expected_competitors if comp in competitors]
            
            if not found_competitors:
                print(f"Warning: None of the expected competitors {expected_competitors} found in {competitors}")
            else:
                print(f"Found expected competitors: {found_competitors}")
            
            # Check analysis perspective
            analysis_perspective = data["market_map"].get("analysis_perspective")
            print(f"Analysis perspective: {analysis_perspective}")
            
            # Store analysis ID for export test
            self.analysis_id = data["market_map"]["id"]
            print(f"Stored analysis ID for export test: {self.analysis_id}")
            
            return True, "Market analysis test passed"
        except Exception as e:
            return False, f"Market analysis test failed: {str(e)}"
    
    def test_analysis_history(self) -> Tuple[bool, str]:
        """Test the analysis history endpoint"""
        try:
            response = self.session.get(f"{self.api_url}/analysis-history")
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            data = response.json()
            print(f"Analysis History Response: {data}")
            
            # Validate response structure
            if "history" not in data:
                return False, "Missing 'history' in response"
            
            # Check if history contains at least one entry
            if not data["history"]:
                print("Warning: Analysis history is empty")
            else:
                print(f"Found {len(data['history'])} entries in analysis history")
            
            return True, "Analysis history test passed"
        except Exception as e:
            return False, f"Analysis history test failed: {str(e)}"
    
    def test_export_market_map(self) -> Tuple[bool, str]:
        """Test the export market map endpoint"""
        if not self.analysis_id:
            print("No analysis ID available, running market analysis first...")
            success, _ = self.test_analyze_market()
            if not success:
                return False, "Failed to get analysis ID for export test"
        
        try:
            response = self.session.get(
                f"{self.api_url}/export-market-map/{self.analysis_id}",
                stream=True
            )
            if response.status_code != 200:
                return False, f"Expected status code 200, got {response.status_code}"
            
            # Check content type
            content_type = response.headers.get('Content-Type')
            expected_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            if content_type != expected_type:
                return False, f"Expected content type '{expected_type}', got '{content_type}'"
            
            # Check content disposition
            content_disposition = response.headers.get('Content-Disposition')
            if not content_disposition or 'attachment' not in content_disposition:
                return False, f"Invalid Content-Disposition: {content_disposition}"
            
            # Check file size
            content_length = int(response.headers.get('Content-Length', 0))
            if content_length <= 0:
                return False, f"Invalid Content-Length: {content_length}"
            
            print(f"Export Response Headers: {dict(response.headers)}")
            print(f"Excel file size: {content_length} bytes")
            
            return True, "Export market map test passed"
        except Exception as e:
            return False, f"Export market map test failed: {str(e)}"


if __name__ == "__main__":
    print("Starting Market Map Generator API Tests with Authentication")
    tester = MarketMapAPITesterWithAuth()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. See details above.")
        sys.exit(1)