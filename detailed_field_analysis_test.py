#!/usr/bin/env python3
"""
Detailed Field Analysis Test for Market Map Generator
Deep dive into the backward compatibility fix to ensure all edge cases are handled
"""

import requests
import json
import os
import sys

def get_backend_url() -> str:
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

def test_detailed_field_analysis():
    """Test detailed field analysis for backward compatibility"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    session = requests.Session()
    
    print(f"Detailed Field Analysis Test at: {api_url}")
    print("=" * 70)
    
    # Get all analyses
    try:
        response = session.get(f"{api_url}/analysis-history")
        if response.status_code != 200:
            print(f"❌ Failed to get analysis history: {response.status_code}")
            return False
        
        data = response.json()
        history = data.get("history", [])
        print(f"Found {len(history)} analyses to test")
        
    except Exception as e:
        print(f"❌ Error getting analysis history: {e}")
        return False
    
    # Test each analysis in detail
    total_analyses = len(history)
    successful_loads = 0
    field_analysis_results = []
    
    for i, analysis in enumerate(history):
        analysis_id = analysis["id"]
        product_name = analysis.get("product_name", "Unknown")
        timestamp = analysis.get("timestamp", "Unknown")
        
        print(f"\n{'='*50}")
        print(f"Analysis {i+1}/{total_analyses}: {product_name}")
        print(f"ID: {analysis_id}")
        print(f"Timestamp: {timestamp}")
        print(f"{'='*50}")
        
        try:
            response = session.get(f"{api_url}/analysis/{analysis_id}")
            if response.status_code != 200:
                print(f"❌ Failed to load: HTTP {response.status_code}")
                field_analysis_results.append({
                    "id": analysis_id,
                    "product_name": product_name,
                    "status": "FAILED_TO_LOAD",
                    "error": f"HTTP {response.status_code}"
                })
                continue
            
            data = response.json()
            successful_loads += 1
            
            # Detailed field analysis
            market_map = data.get("market_map", {})
            visual_map = data.get("visual_map", {})
            
            # Check all fields
            analysis_perspective = market_map.get("analysis_perspective")
            brand_position = market_map.get("brand_position")
            segmentation_by_firmographics = market_map.get("segmentation_by_firmographics")
            
            # Check visual map firmographic segments
            visual_firmographic_segments = visual_map.get("firmographic_segments", [])
            
            print(f"FIELD ANALYSIS:")
            print(f"  analysis_perspective: {analysis_perspective} ({type(analysis_perspective).__name__})")
            print(f"  brand_position: {type(brand_position).__name__} - {'Present' if brand_position else 'None'}")
            print(f"  segmentation_by_firmographics: {type(segmentation_by_firmographics).__name__} with {len(segmentation_by_firmographics) if segmentation_by_firmographics else 0} items")
            print(f"  visual_firmographic_segments: {type(visual_firmographic_segments).__name__} with {len(visual_firmographic_segments)} items")
            
            # Validate field correctness
            issues = []
            
            # Check analysis_perspective
            if analysis_perspective is None:
                issues.append("analysis_perspective is None")
            elif analysis_perspective not in ["existing_brand", "new_entrant"]:
                issues.append(f"analysis_perspective has invalid value: {analysis_perspective}")
            
            # Check brand_position logic
            if analysis_perspective == "existing_brand":
                if brand_position is None:
                    print(f"  NOTE: existing_brand with None brand_position - may be expected for some cases")
                elif not isinstance(brand_position, str):
                    issues.append(f"brand_position should be string for existing_brand, got {type(brand_position)}")
            elif analysis_perspective == "new_entrant":
                if brand_position is not None:
                    print(f"  NOTE: new_entrant with brand_position - unusual but not necessarily wrong")
            
            # Check segmentation_by_firmographics
            if segmentation_by_firmographics is None:
                issues.append("segmentation_by_firmographics is None instead of empty list")
            elif not isinstance(segmentation_by_firmographics, list):
                issues.append(f"segmentation_by_firmographics should be list, got {type(segmentation_by_firmographics)}")
            
            # Check visual map firmographic segments
            if not isinstance(visual_firmographic_segments, list):
                issues.append(f"visual firmographic_segments should be list, got {type(visual_firmographic_segments)}")
            
            # Check consistency between market_map and visual_map firmographics
            market_firmographics_count = len(segmentation_by_firmographics) if segmentation_by_firmographics else 0
            visual_firmographics_count = len(visual_firmographic_segments)
            
            if market_firmographics_count != visual_firmographics_count:
                print(f"  NOTE: Firmographics count mismatch - market_map: {market_firmographics_count}, visual_map: {visual_firmographics_count}")
            
            # Record results
            result = {
                "id": analysis_id,
                "product_name": product_name,
                "status": "PASS" if not issues else "ISSUES",
                "analysis_perspective": analysis_perspective,
                "brand_position_present": brand_position is not None,
                "firmographics_count": market_firmographics_count,
                "visual_firmographics_count": visual_firmographics_count,
                "issues": issues
            }
            field_analysis_results.append(result)
            
            if issues:
                print(f"❌ ISSUES FOUND:")
                for issue in issues:
                    print(f"    - {issue}")
            else:
                print(f"✅ ALL FIELDS VALID")
                
        except Exception as e:
            print(f"❌ Error analyzing analysis: {e}")
            field_analysis_results.append({
                "id": analysis_id,
                "product_name": product_name,
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("DETAILED FIELD ANALYSIS SUMMARY")
    print(f"{'='*70}")
    
    total_tested = len(field_analysis_results)
    passed = len([r for r in field_analysis_results if r["status"] == "PASS"])
    issues = len([r for r in field_analysis_results if r["status"] == "ISSUES"])
    errors = len([r for r in field_analysis_results if r["status"] in ["ERROR", "FAILED_TO_LOAD"]])
    
    print(f"Total analyses: {total_tested}")
    print(f"Passed: {passed}")
    print(f"With issues: {issues}")
    print(f"Errors: {errors}")
    
    # Show issues if any
    if issues > 0:
        print(f"\nANALYSES WITH ISSUES:")
        for result in field_analysis_results:
            if result["status"] == "ISSUES":
                print(f"  {result['product_name']} ({result['id'][:8]}...):")
                for issue in result.get("issues", []):
                    print(f"    - {issue}")
    
    # Show errors if any
    if errors > 0:
        print(f"\nANALYSES WITH ERRORS:")
        for result in field_analysis_results:
            if result["status"] in ["ERROR", "FAILED_TO_LOAD"]:
                print(f"  {result['product_name']} ({result['id'][:8]}...): {result.get('error', 'Unknown error')}")
    
    # Perspective distribution
    perspectives = {}
    for result in field_analysis_results:
        if result["status"] == "PASS" or result["status"] == "ISSUES":
            perspective = result.get("analysis_perspective", "Unknown")
            perspectives[perspective] = perspectives.get(perspective, 0) + 1
    
    print(f"\nANALYSIS PERSPECTIVE DISTRIBUTION:")
    for perspective, count in perspectives.items():
        print(f"  {perspective}: {count}")
    
    # Success criteria
    success = (errors == 0 and issues == 0)
    
    if success:
        print(f"\n✅ ALL FIELD ANALYSIS TESTS PASSED")
        print(f"✅ All {passed} analyses have proper backward compatibility")
    else:
        print(f"\n❌ FIELD ANALYSIS TESTS FAILED")
        print(f"❌ {issues} analyses have field issues, {errors} have errors")
    
    return success

if __name__ == "__main__":
    print("Detailed Field Analysis Test for Market Map Generator")
    print("Testing comprehensive backward compatibility for all fields...")
    print()
    
    success = test_detailed_field_analysis()
    sys.exit(0 if success else 1)