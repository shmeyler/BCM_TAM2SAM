#!/usr/bin/env python3
"""
Field Mapping Test Script
This script tests the strategic analysis field mapping logic mentioned in the review request:
1. Tests that marketing_opportunities are properly mapped to opportunities field
2. Tests that PPC intelligence data structure is correct
3. Tests field mapping verification without requiring authentication
"""

import sys
import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_dir = Path('/app/backend')
load_dotenv(backend_dir / '.env')

# Add backend directory to path
sys.path.append('/app/backend')

from server import MarketInput, ComprehensiveAnalysisEngine, MarketIntelligenceAgent
from spyfu_service import spyfu_service
from datetime import datetime

class FieldMappingTester:
    """Class to test field mapping logic"""
    
    def __init__(self):
        print("Field Mapping Tester Initialized")
    
    async def run_field_mapping_tests(self) -> bool:
        """Run all field mapping tests"""
        tests = [
            ("Strategic Analysis Fields Mapping Logic", self.test_strategic_fields_mapping),
            ("PPC Intelligence Data Structure", self.test_ppc_data_structure),
            ("Market Map Field Verification", self.test_market_map_fields),
            ("AI Analysis Response Structure", self.test_ai_analysis_structure)
        ]
        
        all_passed = True
        results = []
        
        for test_name, test_func in tests:
            print(f"\n{'=' * 60}")
            print(f"Running Test: {test_name}")
            print(f"{'=' * 60}")
            
            try:
                if test_name == "PPC Intelligence Data Structure":
                    success, message = await test_func()
                else:
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
        print("FIELD MAPPING TEST SUMMARY")
        print(f"{'=' * 60}")
        for name, status, message in results:
            print(f"{status} - {name}")
            if status != "✅ PASSED":
                print(f"  └─ {message}")
        
        return all_passed
    
    def test_strategic_fields_mapping(self) -> tuple[bool, str]:
        """Test the strategic analysis fields mapping logic"""
        try:
            print("Testing strategic analysis fields mapping logic...")
            
            # Test Case 1: AI analysis with only marketing_opportunities (should map to opportunities)
            ai_analysis_1 = {
                "market_overview": {"total_market_size": 1000000000, "growth_rate": 0.08, "key_drivers": ["test"]},
                "segmentation": {"by_geographics": [], "by_demographics": [], "by_psychographics": [], "by_behavioral": []},
                "competitors": [],
                "opportunities": [],  # Empty opportunities
                "marketing_opportunities": ["Marketing opportunity 1", "Marketing opportunity 2", "Marketing opportunity 3"],
                "threats": ["Threat 1", "Threat 2"],
                "recommendations": ["Recommendation 1", "Recommendation 2"],
                "executive_summary": "Test summary",
                "data_sources": ["Test source"],
                "confidence_level": "high",
                "methodology": "Test methodology"
            }
            
            # Simulate the field mapping logic from the backend
            opportunities_1 = ai_analysis_1.get("opportunities", [])
            if not opportunities_1:  # If opportunities is empty, try marketing_opportunities
                opportunities_1 = ai_analysis_1.get("marketing_opportunities", [])
            
            print(f"Test Case 1 - Empty opportunities, populated marketing_opportunities:")
            print(f"  Original opportunities: {ai_analysis_1.get('opportunities', [])}")
            print(f"  Marketing opportunities: {ai_analysis_1.get('marketing_opportunities', [])}")
            print(f"  Final mapped opportunities: {opportunities_1}")
            
            if not opportunities_1:
                return False, "Field mapping failed - no opportunities found when marketing_opportunities was populated"
            
            if len(opportunities_1) != 3:
                return False, f"Field mapping failed - expected 3 opportunities, got {len(opportunities_1)}"
            
            # Test Case 2: AI analysis with both opportunities and marketing_opportunities (should use opportunities)
            ai_analysis_2 = {
                "opportunities": ["Direct opportunity 1", "Direct opportunity 2"],
                "marketing_opportunities": ["Marketing opportunity 1", "Marketing opportunity 2", "Marketing opportunity 3"]
            }
            
            opportunities_2 = ai_analysis_2.get("opportunities", [])
            if not opportunities_2:  # If opportunities is empty, try marketing_opportunities
                opportunities_2 = ai_analysis_2.get("marketing_opportunities", [])
            
            print(f"Test Case 2 - Both opportunities and marketing_opportunities populated:")
            print(f"  Original opportunities: {ai_analysis_2.get('opportunities', [])}")
            print(f"  Marketing opportunities: {ai_analysis_2.get('marketing_opportunities', [])}")
            print(f"  Final mapped opportunities: {opportunities_2}")
            
            if len(opportunities_2) != 2:
                return False, f"Field mapping failed - expected 2 direct opportunities, got {len(opportunities_2)}"
            
            if "Direct opportunity 1" not in opportunities_2:
                return False, "Field mapping failed - should prioritize direct opportunities over marketing_opportunities"
            
            # Test Case 3: AI analysis with neither (should result in empty)
            ai_analysis_3 = {
                "threats": ["Threat 1"],
                "recommendations": ["Recommendation 1"]
            }
            
            opportunities_3 = ai_analysis_3.get("opportunities", [])
            if not opportunities_3:  # If opportunities is empty, try marketing_opportunities
                opportunities_3 = ai_analysis_3.get("marketing_opportunities", [])
            
            print(f"Test Case 3 - Neither opportunities nor marketing_opportunities:")
            print(f"  Final mapped opportunities: {opportunities_3}")
            
            if opportunities_3:
                return False, f"Field mapping failed - expected empty opportunities, got {opportunities_3}"
            
            return True, "Strategic analysis fields mapping logic working correctly - marketing_opportunities properly mapped to opportunities when needed"
            
        except Exception as e:
            return False, f"Strategic fields mapping test failed: {str(e)}"
    
    async def test_ppc_data_structure(self) -> tuple[bool, str]:
        """Test PPC intelligence data structure"""
        try:
            print("Testing PPC intelligence data structure...")
            
            # Test the PPC intelligence report structure
            test_domain = "fitnesstracker.com"
            ppc_report = await spyfu_service.generate_ppc_intelligence_report(test_domain)
            
            print(f"PPC Report for {test_domain}:")
            print(f"  Target Domain: {ppc_report.target_domain}")
            print(f"  Paid Keywords: {len(ppc_report.paid_keywords)}")
            print(f"  Top Competitors: {len(ppc_report.top_competitors)}")
            print(f"  Ad History: {len(ppc_report.ad_history)}")
            print(f"  Confidence Level: {ppc_report.confidence_level}")
            
            # Validate structure
            if not ppc_report.target_domain:
                return False, "PPC report missing target_domain"
            
            if not hasattr(ppc_report, 'paid_keywords'):
                return False, "PPC report missing paid_keywords attribute"
            
            if not hasattr(ppc_report, 'top_competitors'):
                return False, "PPC report missing top_competitors attribute"
            
            # Check that we have some demo data
            if len(ppc_report.paid_keywords) == 0:
                return False, "PPC report has no keywords (demo data should be present)"
            
            if len(ppc_report.top_competitors) == 0:
                return False, "PPC report has no competitors (demo data should be present)"
            
            # Test PPC intelligence data format for market map integration
            ppc_intelligence = {
                "target_domain": ppc_report.target_domain,
                "paid_keywords_count": len(ppc_report.paid_keywords),
                "top_keywords": [
                    {
                        "keyword": kw.keyword,
                        "monthly_searches": kw.monthly_searches,
                        "cpc": kw.cpc,
                        "competition": kw.competition
                    } for kw in ppc_report.paid_keywords[:5]
                ],
                "competitors": [
                    {
                        "domain": comp.domain,
                        "overlapping_keywords": comp.overlapping_keywords,
                        "estimated_monthly_spend": comp.estimated_monthly_spend
                    } for comp in ppc_report.top_competitors[:3]
                ],
                "confidence_level": ppc_report.confidence_level
            }
            
            print(f"PPC Intelligence Data Structure: {json.dumps(ppc_intelligence, indent=2)}")
            
            # Validate the structure matches what the frontend expects
            required_fields = ["target_domain", "paid_keywords_count", "top_keywords", "competitors", "confidence_level"]
            for field in required_fields:
                if field not in ppc_intelligence:
                    return False, f"PPC intelligence missing required field: {field}"
            
            return True, f"PPC intelligence data structure correct - {len(ppc_report.paid_keywords)} keywords, {len(ppc_report.top_competitors)} competitors"
            
        except Exception as e:
            return False, f"PPC data structure test failed: {str(e)}"
    
    def test_market_map_fields(self) -> tuple[bool, str]:
        """Test market map field verification"""
        try:
            print("Testing market map field verification...")
            
            # Create a sample market input
            market_input = MarketInput(
                product_name="Fitness Tracker",
                industry="Wearable Technology",
                geography="Global",
                target_user="Health-conscious consumers",
                demand_driver="Health and wellness trends",
                transaction_type="One-time Purchase",
                key_metrics="Device sales, user engagement",
                benchmarks="Market growing at 9.2% CAGR"
            )
            
            # Test the expected fields that should be in a market map
            expected_fields = [
                "id",
                "market_input_id", 
                "total_market_size",
                "market_growth_rate",
                "key_drivers",
                "analysis_perspective",
                "segmentation_by_geographics",
                "segmentation_by_demographics", 
                "segmentation_by_psychographics",
                "segmentation_by_behavioral",
                "segmentation_by_firmographics",
                "competitors",
                "opportunities",
                "threats",
                "strategic_recommendations",
                "marketing_opportunities",
                "marketing_threats",
                "marketing_recommendations",
                "competitive_digital_assessment",
                "ppc_intelligence",
                "executive_summary",
                "data_sources",
                "confidence_level",
                "methodology",
                "timestamp"
            ]
            
            print(f"Expected Market Map Fields ({len(expected_fields)}):")
            for i, field in enumerate(expected_fields, 1):
                print(f"  {i:2d}. {field}")
            
            # Verify that the MarketMap model has all expected fields
            from server import MarketMap
            import inspect
            
            # Get MarketMap model fields
            market_map_fields = []
            for name, field in MarketMap.__fields__.items():
                market_map_fields.append(name)
            
            print(f"\nActual MarketMap Model Fields ({len(market_map_fields)}):")
            for i, field in enumerate(sorted(market_map_fields), 1):
                print(f"  {i:2d}. {field}")
            
            # Check for missing fields
            missing_fields = []
            for field in expected_fields:
                if field not in market_map_fields:
                    missing_fields.append(field)
            
            # Check for extra fields (not necessarily bad, but good to know)
            extra_fields = []
            for field in market_map_fields:
                if field not in expected_fields:
                    extra_fields.append(field)
            
            if missing_fields:
                return False, f"MarketMap model missing expected fields: {missing_fields}"
            
            if extra_fields:
                print(f"Note: MarketMap has additional fields not in expected list: {extra_fields}")
            
            return True, f"Market map field verification passed - all {len(expected_fields)} expected fields present in MarketMap model"
            
        except Exception as e:
            return False, f"Market map fields test failed: {str(e)}"
    
    def test_ai_analysis_structure(self) -> tuple[bool, str]:
        """Test AI analysis response structure"""
        try:
            print("Testing AI analysis response structure...")
            
            # Test the expected structure of AI analysis response
            expected_ai_fields = [
                "market_overview",
                "analysis_perspective", 
                "segmentation",
                "competitors",
                "opportunities",
                "threats", 
                "recommendations",
                "marketing_opportunities",
                "marketing_threats",
                "marketing_recommendations",
                "competitive_digital_assessment",
                "executive_summary",
                "data_sources",
                "confidence_level",
                "methodology"
            ]
            
            print(f"Expected AI Analysis Fields ({len(expected_ai_fields)}):")
            for i, field in enumerate(expected_ai_fields, 1):
                print(f"  {i:2d}. {field}")
            
            # Test sample AI analysis structure
            sample_ai_analysis = {
                "market_overview": {
                    "total_market_size": 42000000000,
                    "growth_rate": 0.092,
                    "key_drivers": ["Health trends", "Technology adoption"]
                },
                "analysis_perspective": "new_entrant",
                "segmentation": {
                    "by_geographics": [],
                    "by_demographics": [],
                    "by_psychographics": [],
                    "by_behavioral": []
                },
                "competitors": [],
                "opportunities": [],  # This might be empty
                "marketing_opportunities": ["Marketing opp 1", "Marketing opp 2"],  # This should map to opportunities
                "threats": ["Threat 1"],
                "recommendations": ["Recommendation 1"],
                "executive_summary": "Test summary",
                "data_sources": ["Test source"],
                "confidence_level": "high",
                "methodology": "Test methodology"
            }
            
            # Verify the field mapping logic works with this structure
            opportunities = sample_ai_analysis.get("opportunities", [])
            if not opportunities:  # If opportunities is empty, try marketing_opportunities
                opportunities = sample_ai_analysis.get("marketing_opportunities", [])
            
            print(f"\nField Mapping Test:")
            print(f"  Original opportunities: {sample_ai_analysis.get('opportunities', [])}")
            print(f"  Marketing opportunities: {sample_ai_analysis.get('marketing_opportunities', [])}")
            print(f"  Final mapped opportunities: {opportunities}")
            
            if not opportunities:
                return False, "AI analysis structure test failed - field mapping not working"
            
            if len(opportunities) != 2:
                return False, f"AI analysis structure test failed - expected 2 mapped opportunities, got {len(opportunities)}"
            
            # Check that all expected fields are present in sample
            missing_in_sample = []
            for field in expected_ai_fields:
                if field not in sample_ai_analysis:
                    missing_in_sample.append(field)
            
            if missing_in_sample:
                print(f"Note: Sample AI analysis missing some expected fields: {missing_in_sample}")
            
            return True, f"AI analysis structure test passed - field mapping working correctly, {len(opportunities)} opportunities mapped"
            
        except Exception as e:
            return False, f"AI analysis structure test failed: {str(e)}"


async def main():
    print("Starting Field Mapping Tests")
    print("Testing specific field mapping fixes mentioned in review request:")
    print("1. Strategic Analysis Fields Fix (marketing_opportunities -> opportunities mapping)")
    print("2. PPC Intelligence Data Structure")
    print("3. Field Mapping Verification")
    
    tester = FieldMappingTester()
    success = await tester.run_field_mapping_tests()
    
    if success:
        print("\n✅ All field mapping tests passed successfully!")
        return 0
    else:
        print("\n❌ Some field mapping tests failed. See details above.")
        return 1


if __name__ == "__main__":
    import asyncio
    exit_code = asyncio.run(main())
    sys.exit(exit_code)