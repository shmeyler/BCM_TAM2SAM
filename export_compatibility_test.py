#!/usr/bin/env python3
"""
Export Compatibility Test for Market Map Generator
Test that export functionality works with both old and new analysis structures
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

def test_export_compatibility():
    """Test export functionality with backward compatibility"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    session = requests.Session()
    
    print(f"Export Compatibility Test at: {api_url}")
    print("=" * 60)
    
    # Get analysis history
    try:
        response = session.get(f"{api_url}/analysis-history")
        if response.status_code != 200:
            print(f"❌ Failed to get analysis history: {response.status_code}")
            return False
        
        data = response.json()
        history = data.get("history", [])
        print(f"Found {len(history)} analyses to test export functionality")
        
    except Exception as e:
        print(f"❌ Error getting analysis history: {e}")
        return False
    
    if len(history) == 0:
        print("❌ No analyses found to test export")
        return False
    
    # Test export for different types of analyses
    export_results = []
    
    # Test first 3 analyses
    test_analyses = history[:3]
    
    for i, analysis in enumerate(test_analyses):
        analysis_id = analysis["id"]
        product_name = analysis.get("product_name", "Unknown")
        
        print(f"\n{'='*40}")
        print(f"Testing Export {i+1}: {product_name}")
        print(f"Analysis ID: {analysis_id}")
        print(f"{'='*40}")
        
        try:
            # First, verify the analysis can be loaded
            response = session.get(f"{api_url}/analysis/{analysis_id}")
            if response.status_code != 200:
                print(f"❌ Cannot load analysis for export test: HTTP {response.status_code}")
                export_results.append({
                    "id": analysis_id,
                    "product_name": product_name,
                    "status": "FAILED_TO_LOAD_ANALYSIS"
                })
                continue
            
            analysis_data = response.json()
            market_map = analysis_data.get("market_map", {})
            
            # Check the fields that might affect export
            analysis_perspective = market_map.get("analysis_perspective")
            brand_position = market_map.get("brand_position")
            segmentation_by_firmographics = market_map.get("segmentation_by_firmographics", [])
            
            print(f"Analysis fields:")
            print(f"  - analysis_perspective: {analysis_perspective}")
            print(f"  - brand_position: {'Present' if brand_position else 'None'}")
            print(f"  - firmographics segments: {len(segmentation_by_firmographics)}")
            
            # Test Excel export
            print(f"Testing Excel export...")
            export_response = session.get(f"{api_url}/export-market-map/{analysis_id}")
            
            if export_response.status_code != 200:
                print(f"❌ Excel export failed: HTTP {export_response.status_code}")
                export_results.append({
                    "id": analysis_id,
                    "product_name": product_name,
                    "status": "EXPORT_FAILED",
                    "error": f"HTTP {export_response.status_code}"
                })
                continue
            
            # Check export response
            content_type = export_response.headers.get('Content-Type')
            content_length = int(export_response.headers.get('Content-Length', 0))
            content_disposition = export_response.headers.get('Content-Disposition', '')
            
            print(f"Export response:")
            print(f"  - Content-Type: {content_type}")
            print(f"  - Content-Length: {content_length} bytes")
            print(f"  - Content-Disposition: {content_disposition}")
            
            # Validate export
            expected_content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            
            issues = []
            if content_type != expected_content_type:
                issues.append(f"Wrong content type: {content_type}")
            if content_length <= 0:
                issues.append(f"Invalid content length: {content_length}")
            if 'attachment' not in content_disposition:
                issues.append(f"Missing attachment in content disposition")
            
            if issues:
                print(f"❌ Export validation failed:")
                for issue in issues:
                    print(f"    - {issue}")
                export_results.append({
                    "id": analysis_id,
                    "product_name": product_name,
                    "status": "EXPORT_VALIDATION_FAILED",
                    "issues": issues
                })
            else:
                print(f"✅ Excel export successful")
                export_results.append({
                    "id": analysis_id,
                    "product_name": product_name,
                    "status": "SUCCESS",
                    "file_size": content_length
                })
                
        except Exception as e:
            print(f"❌ Error testing export: {e}")
            export_results.append({
                "id": analysis_id,
                "product_name": product_name,
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("EXPORT COMPATIBILITY TEST SUMMARY")
    print(f"{'='*60}")
    
    total_tested = len(export_results)
    successful = len([r for r in export_results if r["status"] == "SUCCESS"])
    failed = total_tested - successful
    
    print(f"Total exports tested: {total_tested}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print(f"\nSUCCESSFUL EXPORTS:")
        for result in export_results:
            if result["status"] == "SUCCESS":
                file_size = result.get("file_size", 0)
                print(f"  ✅ {result['product_name']} - {file_size} bytes")
    
    if failed > 0:
        print(f"\nFAILED EXPORTS:")
        for result in export_results:
            if result["status"] != "SUCCESS":
                error_info = result.get("error", result.get("issues", "Unknown error"))
                print(f"  ❌ {result['product_name']} - {result['status']}: {error_info}")
    
    success = (failed == 0)
    
    if success:
        print(f"\n✅ ALL EXPORT COMPATIBILITY TESTS PASSED")
        print(f"✅ All {successful} exports work correctly with backward compatibility")
    else:
        print(f"\n❌ EXPORT COMPATIBILITY TESTS FAILED")
        print(f"❌ {failed} exports failed")
    
    return success

if __name__ == "__main__":
    print("Export Compatibility Test for Market Map Generator")
    print("Testing that export functionality works with backward compatibility...")
    print()
    
    success = test_export_compatibility()
    sys.exit(0 if success else 1)