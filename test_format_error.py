#!/usr/bin/env python3
"""
Test script to reproduce the Invalid format specifier error
"""

# Simulate the curated data structure
curated_data = {
    'sources': ["Brewers Association", "IBISWorld"],
    'confidence': 'high'
}

# This should work fine
print("Testing normal case:")
try:
    result = f"Curated market database analysis with {curated_data['confidence']} confidence"
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test with the sources field
print("\nTesting sources field:")
try:
    result = f"Sources: {curated_data['sources']}"
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test the actual problematic line
print("\nTesting the actual problematic scenario:")
try:
    # This might be where the error occurs if sources contains format specifiers
    test_sources = ["Gartner Market Research", "url: https://www.gartner.com/en/research"]
    result = f"Analysis from {test_sources}"
    print(f"✅ Success: {result}")
except Exception as e:
    print(f"❌ Error: {e}")