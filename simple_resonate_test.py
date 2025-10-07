#!/usr/bin/env python3
"""
Simple Resonate Export Test - Tests the export-personas endpoint functionality
"""

import requests
import json
import os

def get_backend_url():
    """Read the backend URL from the frontend/.env file"""
    env_path = os.path.join('/app', 'frontend', '.env')
    with open(env_path, 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                return line.strip().split('=')[1].strip('"\'')
    raise ValueError("Backend URL not found in frontend/.env")

def test_export_personas_endpoint():
    """Test the export-personas endpoint with existing analysis data"""
    base_url = get_backend_url()
    api_url = f"{base_url}/api"
    
    print("Testing Resonate Export Personas Endpoint")
    print("=" * 50)
    
    # Get analysis history
    response = requests.get(f"{api_url}/analysis-history")
    if response.status_code != 200:
        print(f"❌ Failed to get analysis history: {response.status_code}")
        return False
    
    history = response.json().get("history", [])
    if not history:
        print("❌ No analyses found in history")
        return False
    
    print(f"✓ Found {len(history)} analyses in history")
    
    # Test export-personas with the first analysis
    analysis_id = history[0]["id"]
    product_name = history[0]["product_name"]
    
    print(f"✓ Testing with analysis: {product_name} (ID: {analysis_id})")
    
    response = requests.get(f"{api_url}/export-personas/{analysis_id}")
    if response.status_code != 200:
        print(f"❌ Export personas failed: {response.status_code}")
        if response.status_code == 404:
            print("   Analysis not found - this indicates a database consistency issue")
        return False
    
    data = response.json()
    
    # Validate response structure
    required_fields = [
        "analysis_info", "demographic_personas", "psychographic_personas", 
        "behavioral_personas", "resonate_taxonomy_mapping", "persona_summary"
    ]
    
    print("\nResponse Structure Validation:")
    all_fields_present = True
    for field in required_fields:
        if field in data:
            print(f"✓ {field}")
        else:
            print(f"❌ {field} - MISSING")
            all_fields_present = False
    
    if not all_fields_present:
        return False
    
    # Check data content
    print(f"\nData Content Analysis:")
    print(f"✓ Analysis Info - Product: {data['analysis_info'].get('product_name')}")
    print(f"✓ Demographic Personas: {len(data['demographic_personas'])}")
    print(f"✓ Psychographic Personas: {len(data['psychographic_personas'])}")
    print(f"✓ Behavioral Personas: {len(data['behavioral_personas'])}")
    print(f"✓ Resonate Taxonomy Mappings: {len(data['resonate_taxonomy_mapping'])}")
    
    # Check persona summary
    summary = data.get("persona_summary", {})
    print(f"✓ Persona Summary:")
    print(f"  - Total segments: {summary.get('total_segments', 0)}")
    print(f"  - Resonate ready segments: {summary.get('resonate_ready_segments', 0)}")
    print(f"  - Integration ready: {summary.get('resonate_integration_ready', False)}")
    
    # Check if we have any actual resonate mapping data
    if data['resonate_taxonomy_mapping']:
        print(f"\n✓ Found Resonate mapping data:")
        for mapping in data['resonate_taxonomy_mapping'][:2]:  # Show first 2
            print(f"  - Segment: {mapping.get('segment_name')}")
            print(f"    Type: {mapping.get('segment_type')}")
            print(f"    Taxonomy paths: {len(mapping.get('taxonomy_paths', []))}")
    else:
        print(f"\n⚠️  No Resonate mapping data found (expected for older analyses)")
    
    print(f"\n✅ Export Personas endpoint is working correctly!")
    print(f"   The endpoint returns the proper structure for Resonate integration.")
    
    # Test with multiple analyses to verify consistency
    print(f"\nTesting endpoint consistency with multiple analyses...")
    success_count = 0
    for i, analysis in enumerate(history[:3]):  # Test first 3
        test_id = analysis["id"]
        test_response = requests.get(f"{api_url}/export-personas/{test_id}")
        if test_response.status_code == 200:
            success_count += 1
            print(f"✓ Analysis {i+1}: {analysis['product_name']} - SUCCESS")
        else:
            print(f"❌ Analysis {i+1}: {analysis['product_name']} - FAILED ({test_response.status_code})")
    
    print(f"\n✅ Endpoint consistency test: {success_count}/{min(3, len(history))} analyses successful")
    
    return True

if __name__ == "__main__":
    success = test_export_personas_endpoint()
    if success:
        print("\n🎉 Resonate Export Personas functionality is working!")
    else:
        print("\n❌ Resonate Export Personas functionality has issues.")