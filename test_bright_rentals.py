#!/usr/bin/env python3
"""
Test Bright Event Rentals market analysis to check for real insights vs generic content
"""

import requests
import json
import sys

def test_bright_rentals_analysis():
    # Test data for Bright Rentals 
    test_data = {
        'product_name': 'Bright Event Rentals',
        'industry': 'Event Equipment Rental',
        'geography': 'United States',
        'target_user': 'Event planners and corporate clients',
        'demand_driver': 'Growing event and wedding industry',
        'transaction_type': 'Rental Services',
        'key_metrics': 'Rental volume, customer satisfaction',
        'benchmarks': 'Industry growth at 5.8% annually'
    }

    # Get backend URL
    with open('/app/frontend/.env', 'r') as f:
        for line in f:
            if line.startswith('REACT_APP_BACKEND_URL='):
                backend_url = line.strip().split('=')[1].strip('"\'')
                break

    api_url = f'{backend_url}/api'
    print('Testing Bright Event Rentals Market Analysis...')
    print(f'API URL: {api_url}')

    try:
        print('\n🔄 Starting market analysis...')
        response = requests.post(f'{api_url}/analyze-market', json=test_data, timeout=180)
        print(f'Response Status: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if we got real insights or generic fallback
            market_map = data.get('market_map', {})
            competitors = market_map.get('competitors', [])
            exec_summary = market_map.get('executive_summary', '')
            
            print('\n' + '='*70)
            print('BRIGHT EVENT RENTALS - ANALYSIS RESULTS')
            print('='*70)
            
            print(f'Analysis Method: {"AI-Powered" if data.get("ai_analysis_used", False) else "Fallback Analysis"}')
            print(f'Confidence Level: {market_map.get("confidence_level", "Unknown")}')
            
            # Check competitors
            print(f'\n🏢 COMPETITORS ({len(competitors)} found):')
            if competitors:
                for i, comp in enumerate(competitors[:5], 1):
                    name = comp.get('name', 'Unknown')
                    share = comp.get('market_share', 'N/A')
                    strengths = comp.get('strengths', [])
                    print(f'  {i}. {name} - {share}% market share')
                    if strengths:
                        print(f'     Strengths: {strengths[:2]}')
            else:
                print('  ❌ No competitors found')
            
            # Check executive summary quality
            print(f'\n📄 EXECUTIVE SUMMARY QUALITY:')
            print(f'  Length: {len(exec_summary)} characters')
            print(f'  Contains "Bright": {"Bright" in exec_summary}')
            print(f'  Contains "event": {"event" in exec_summary.lower()}')
            print(f'  Contains "rental": {"rental" in exec_summary.lower()}')
            
            # Check for generic vs specific content
            generic_indicators = ['Company A', 'Company B', 'Generic', 'Placeholder', 'Example']
            has_generic = any(indicator in exec_summary for indicator in generic_indicators)
            print(f'  Has Generic Content: {"❌ Yes" if has_generic else "✅ No"}')
            
            # Show first 300 chars of summary
            print(f'\n📝 EXECUTIVE SUMMARY PREVIEW:')
            print(f'  "{exec_summary[:300]}..."')
            
            # Check segmentation quality
            demographics = market_map.get('segmentation_by_demographics', [])
            print(f'\n👥 DEMOGRAPHIC SEGMENTS ({len(demographics)} found):')
            for i, seg in enumerate(demographics[:3], 1):
                print(f'  {i}. {seg.get("name", "Unnamed")}')
                print(f'     Size: ${seg.get("size_estimate", 0) / 1000000:.0f}M')
                
            # Check if analysis seems realistic
            total_market = market_map.get('total_market_size', 0)
            print(f'\n💰 MARKET SIZING:')
            print(f'  Total Market Size: ${total_market / 1000000000:.1f}B')
            print(f'  TAM: ${market_map.get("tam", 0) / 1000000000:.1f}B')
            print(f'  SAM: ${market_map.get("sam", 0) / 1000000000:.1f}B')
            print(f'  SOM: ${market_map.get("som", 0) / 1000000000:.1f}B')
            
            # Check brand names in competitors
            print(f'\n🏷️ BRAND NAME ANALYSIS:')
            brand_names = [comp.get('name', '') for comp in competitors]
            real_brands = []
            generic_brands = []
            
            for name in brand_names:
                if any(generic in name for generic in ['Company', 'Corp', 'Inc.', 'LLC', 'Generic']):
                    generic_brands.append(name)
                else:
                    real_brands.append(name)
            
            print(f'  Real Brand Names: {len(real_brands)} - {real_brands[:5]}')
            print(f'  Generic Names: {len(generic_brands)} - {generic_brands[:3]}')
            
            # Overall quality assessment
            quality_score = 0
            if len(competitors) >= 3: quality_score += 1
            if len(exec_summary) > 500: quality_score += 1
            if not has_generic: quality_score += 1
            if len(demographics) >= 3: quality_score += 1
            if total_market > 1000000000: quality_score += 1  # > $1B seems reasonable
            if len(real_brands) > len(generic_brands): quality_score += 1
            
            print(f'\n🎯 ANALYSIS QUALITY SCORE: {quality_score}/6')
            if quality_score >= 5:
                print('  ✅ EXCELLENT QUALITY - Real insights and specific brands')
            elif quality_score >= 3:
                print('  ⚠️ MEDIUM QUALITY - Some generic content, needs improvement')
            else:
                print('  ❌ LOW QUALITY - Mostly generic/fallback data')
                
            # Specific issue diagnosis
            print(f'\n🔍 ISSUE DIAGNOSIS:')
            if len(competitors) == 0:
                print('  ❌ No competitors found - AI may not have industry knowledge')
            elif len(generic_brands) > len(real_brands):
                print('  ⚠️ Too many generic competitor names - AI using fallback data')
            if len(exec_summary) < 300:
                print('  ⚠️ Executive summary too short - may be using template')
            if has_generic:
                print('  ⚠️ Generic placeholders found - AI prompt may need refinement')
                
        elif response.status_code == 401:
            print('❌ Authentication required - please log into the main app first')
        else:
            print(f'❌ Analysis failed: {response.status_code}')
            print(f'Response: {response.text[:500]}')
            
    except Exception as e:
        print(f'❌ Error: {e}')
        return False
    
    return True

if __name__ == "__main__":
    test_bright_rentals_analysis()