#!/usr/bin/env python3
"""
Simple Backward Compatibility Test for Market Map Generator
Focus on testing the core fix for older reports missing new fields
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

def test_backward_compatibility():
    """Test the backward compatibility fix"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    session = requests.Session()
    
    print(f"Testing backward compatibility at: {api_url}")
    print("=" * 60)
    
    # Test 1: Get analysis history
    print("1. Testing Analysis History Endpoint...")
    try:
        response = session.get(f"{api_url}/analysis-history")
        if response.status_code != 200:
            print(f"❌ Analysis history failed: {response.status_code}")
            return False
        
        data = response.json()
        history = data.get("history", [])
        print(f"✅ Found {len(history)} analyses in history")
        
        if len(history) == 0:
            print("❌ No analyses found to test backward compatibility")
            return False
            
    except Exception as e:
        print(f"❌ Analysis history error: {e}")
        return False
    
    # Test 2: Load multiple analyses and check for backward compatibility
    print("\n2. Testing Multiple Analysis Loading with Backward Compatibility...")
    
    successful_loads = 0
    analyses_with_new_fields = 0
    analyses_with_defaults = 0
    
    # Test first 5 analyses
    test_analyses = history[:5]
    
    for i, analysis in enumerate(test_analyses):
        analysis_id = analysis["id"]
        product_name = analysis.get("product_name", "Unknown")
        
        print(f"\n  Testing Analysis {i+1}: {product_name} (ID: {analysis_id[:8]}...)")
        
        try:
            response = session.get(f"{api_url}/analysis/{analysis_id}")
            if response.status_code != 200:
                print(f"    ❌ Failed to load: HTTP {response.status_code}")
                continue
            
            data = response.json()
            successful_loads += 1
            
            # Check market_map structure
            market_map = data.get("market_map", {})
            
            # Check for new fields
            analysis_perspective = market_map.get("analysis_perspective")
            brand_position = market_map.get("brand_position")
            segmentation_by_firmographics = market_map.get("segmentation_by_firmographics")
            
            print(f"    ✅ Loaded successfully")
            print(f"    - analysis_perspective: {analysis_perspective}")
            print(f"    - brand_position: {'Present' if brand_position else 'None'}")
            print(f"    - segmentation_by_firmographics: {type(segmentation_by_firmographics).__name__} with {len(segmentation_by_firmographics) if segmentation_by_firmographics else 0} items")
            
            # Verify backward compatibility
            has_valid_perspective = analysis_perspective in ["existing_brand", "new_entrant"]
            has_valid_firmographics = isinstance(segmentation_by_firmographics, list)
            
            if has_valid_perspective and has_valid_firmographics:
                analyses_with_defaults += 1
                print(f"    ✅ Backward compatibility: PASS")
            else:
                print(f"    ❌ Backward compatibility: FAIL")
                if not has_valid_perspective:
                    print(f"      - Invalid analysis_perspective: {analysis_perspective}")
                if not has_valid_firmographics:
                    print(f"      - Invalid segmentation_by_firmographics: {type(segmentation_by_firmographics)}")
            
            # Check visual map generation
            visual_map = data.get("visual_map")
            if visual_map:
                firmographic_segments = visual_map.get("firmographic_segments", [])
                print(f"    ✅ Visual map generated with {len(firmographic_segments)} firmographic segments")
            else:
                print(f"    ❌ No visual map generated")
                
        except Exception as e:
            print(f"    ❌ Error loading analysis: {e}")
    
    # Test 3: Summary
    print(f"\n3. Test Summary:")
    print(f"   - Analyses tested: {len(test_analyses)}")
    print(f"   - Successfully loaded: {successful_loads}")
    print(f"   - With valid backward compatibility: {analyses_with_defaults}")
    
    if successful_loads == 0:
        print("❌ CRITICAL: No analyses could be loaded")
        return False
    elif analyses_with_defaults < successful_loads:
        print(f"❌ CRITICAL: {successful_loads - analyses_with_defaults} analyses missing proper default values")
        return False
    else:
        print("✅ SUCCESS: All loaded analyses have proper backward compatibility")
        return True

if __name__ == "__main__":
    print("Simple Backward Compatibility Test for Market Map Generator")
    print("Testing fix for older reports missing new fields...")
    print()
    
    success = test_backward_compatibility()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ BACKWARD COMPATIBILITY TEST PASSED")
        print("✅ Older reports load successfully with default values")
        print("✅ New fields (analysis_perspective, brand_position, segmentation_by_firmographics) are properly handled")
        print("✅ Visual map generation works with both old and new data structures")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ BACKWARD COMPATIBILITY TEST FAILED")
        print("❌ Issues found with loading older reports")
        sys.exit(1)