#!/usr/bin/env python3
"""
Test script for TCG TECH suggestion system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import detect_digital_solution_need, detect_techtech_query, get_techtech_suggestion_context

def test_digital_solution_detection():
    """Test digital solution need detection"""
    
    print("🌐 Testing Digital Solution Detection")
    print("=" * 50)
    
    test_cases = [
        "enaku oru website develop pananu enoda groccery shop ku",
        "enoda business ku oru app develop panalam nu irruka",
        "tcgtech entha website ah develop pani tharuvagala enoda budget only 7k tha",
        "I need a mobile app for my business",
        "custom software development required",
        "how are you today",
        "what is your name"
    ]
    
    for i, message in enumerate(test_cases, 1):
        is_digital = detect_digital_solution_need(message)
        is_techtech = detect_techtech_query(message)
        
        print(f"\nTest {i}: '{message}'")
        print(f"  Digital solution need: {is_digital}")
        print(f"  TCG TECH query: {is_techtech}")
        
        if is_digital and not is_techtech:
            print("  → Should suggest TCG TECH!")
        elif is_techtech:
            print("  → Should provide TCG TECH info!")

def test_suggestion_context():
    """Test TCG TECH suggestion context"""
    
    print("\n🏢 Testing TCG TECH Suggestion Context")
    print("=" * 50)
    
    context = get_techtech_suggestion_context()
    print("Suggestion context generated:")
    print(context)

if __name__ == "__main__":
    test_digital_solution_detection()
    test_suggestion_context()
    
    print("\n✅ All tests completed!")
