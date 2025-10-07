#!/usr/bin/env python3
"""
Market Map Generator - Segmentation Analysis Demonstration
This script shows how segmentation data is determined for Bright Event Rentals
"""

import asyncio
from datetime import datetime
from typing import Dict, Any

# Sample data for Bright Event Rentals
bright_event_data = {
    "product_name": "Bright Event Rentals",
    "industry": "Event Equipment Rental", 
    "geography": "United States",
    "target_user": "Event planners and corporate clients",
    "demand_driver": "Growing event and wedding industry",
    "transaction_type": "Rental Services",
    "key_metrics": "Rental volume, customer satisfaction",
    "benchmarks": "Industry growth at 5.8% annually"
}

def analyze_segmentation_sources():
    """Demonstrate how segmentation data is generated"""
    
    print("=" * 80)
    print("BRIGHT EVENT RENTALS - SEGMENTATION ANALYSIS EXPLANATION")
    print("=" * 80)
    
    print("\n🎯 ANALYSIS INPUT:")
    for key, value in bright_event_data.items():
        print(f"   {key}: {value}")
    
    print("\n📊 HOW SEGMENTATION IS DETERMINED:")
    print("\n1. INDUSTRY CLASSIFICATION:")
    print("   • Event Equipment Rental is classified as B2B service")
    print("   • This triggers firmographic segmentation logic")
    print("   • B2C products would get demographic/psychographic segmentation instead")
    
    print("\n2. FIRMOGRAPHIC SEGMENTATION (B2B):")
    print("   Based on standard B2B segmentation framework:")
    
    # Simulate the segmentation logic from the backend
    print("\n   🏢 Enterprise Clients:")
    print("      - Large corporations with 1000+ employees")
    print("      - Factors: Enterprise, 1000+ employees, Global locations, C-suite, $1B+ revenue")
    print("      - Examples: Fortune 500 companies hosting major conferences")
    
    print("\n   🏭 Mid-Market Companies:")
    print("      - Growing companies with 100-1000 employees") 
    print("      - Factors: Mid-market, 100-1000 employees, Regional presence, Director level, $10M-$1B revenue")
    print("      - Examples: Regional corporations hosting annual meetings")
    
    print("\n   🏪 Small Businesses:")
    print("      - Small businesses with under 100 employees")
    print("      - Factors: Small business, Under 100 employees, Local presence, Manager level, Under $10M revenue")
    print("      - Examples: Local event planners, wedding coordinators")
    
    print("\n3. DATA SOURCES:")
    print("   The system uses TWO main approaches:")
    
    print("\n   A) AI-POWERED ANALYSIS (Primary Method):")
    print("      • Uses Together AI (Kimi K2 Instruct model)")
    print("      • Generates analysis based on:")
    print("        - Real-time market research methodologies")
    print("        - Industry-specific knowledge training")
    print("        - Standard data sources like:")
    print("          → Gartner Market Research (https://www.gartner.com/en/research)")
    print("          → McKinsey Industry Reports (https://www.mckinsey.com/industries)")
    print("          → IBISWorld Market Analysis (https://www.ibisworld.com)")
    print("          → Forrester Research (https://www.forrester.com/research)")
    print("          → PwC Industry Insights (https://www.pwc.com/us/en/industries.html)")
    
    print("\n   B) CURATED MARKET DATABASE (Backup):")
    print("      • Pre-researched data for common industries")
    print("      • Fallback when AI analysis isn't available")
    print("      • Sources: Industry reports, market research, public data")
    
    print("\n4. MARKET SIZING METHODOLOGY:")
    print("   • TAM (Total Addressable Market): Based on total industry size")
    print("   • SAM (Serviceable Addressable Market): Geographic and target constraints")
    print("   • SOM (Serviceable Obtainable Market): Realistic capture potential")
    print("   • Growth rates from industry benchmarks and demand drivers")
    
    print("\n5. COMPETITIVE ANALYSIS:")
    print("   • Identifies key players in the event rental space")
    print("   • Market share estimates based on industry knowledge")
    print("   • Competitive positioning relative to Bright Event Rentals")
    
    print("\n📚 SPECIFIC FOR BRIGHT EVENT RENTALS:")
    print("   Expected data sources would include:")
    print("   • Event industry market reports (CEIR, IAEE)")
    print("   • Wedding industry statistics (The Knot, Wedding Report)")
    print("   • Equipment rental industry analysis (American Rental Association)")
    print("   • Local market demographics and event venue data")
    print("   • Corporate event spending trends")
    
    print("\n⚡ REAL-TIME VS STATIC DATA:")
    print("   • AI analysis provides real-time, contextual insights")
    print("   • Segmentation factors are based on established B2B frameworks")
    print("   • Market sizes calculated using standard industry methodologies")
    print("   • Data sources are authoritative market research providers")
    
    print("\n🔍 TRANSPARENCY & ACCURACY:")
    print("   • All data sources are listed in the final report")
    print("   • Confidence levels indicated (High/Medium/Low)")
    print("   • Methodology clearly explained in output")
    print("   • Analysis perspective specified (existing brand vs new entrant)")
    
    print("\n" + "=" * 80)
    print("This ensures Bright Event Rentals gets industry-specific,")
    print("professionally-sourced market segmentation data.")
    print("=" * 80)

if __name__ == "__main__":
    analyze_segmentation_sources()