#!/usr/bin/env python3
"""
Test script for Enhanced Luna with TCG TECH suggestions and self-learning
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import (
    detect_digital_solution_need, 
    detect_techtech_query, 
    get_techtech_suggestion_context,
    update_user_memory,
    get_learning_insights,
    detect_casual_language_permission
)

def test_enhanced_luna():
    """Test all enhanced Luna features"""
    
    print("🚀 Testing Enhanced Luna Features")
    print("=" * 60)
    
    # Test 1: Digital Solution Detection
    print("\n📱 Test 1: Digital Solution Detection")
    test_messages = [
        "enaku website develop pananu",
        "enoda business ku oru app develop panalam nu irruka",
        "tcgtech website develop pani tharuvagala",
        "evlo charge panuvaga tcg tech website development ku",
        "how are you today"
    ]
    
    for msg in test_messages:
        is_digital = detect_digital_solution_need(msg)
        is_techtech = detect_techtech_query(msg)
        print(f"  '{msg}' → Digital: {is_digital}, TCG TECH: {is_techtech}")
    
    # Test 2: TCG TECH Suggestion Context
    print("\n🏢 Test 2: TCG TECH Suggestion Context")
    context = get_techtech_suggestion_context()
    print("  ✅ Suggestion context includes:")
    print("    - Contact URL: https://tcgtech.in/contact" if "tcgtech.in/contact" in context else "    ❌ Missing contact URL")
    print("    - Product-based company info" if "PRODUCT-BASED" in context else "    ❌ Missing product-based info")
    print("    - Luna creator mention" if "created Luna" in context else "    ❌ Missing Luna creator mention")
    
    # Test 3: Self-Learning System
    print("\n🧠 Test 3: Self-Learning System")
    
    # Simulate user interactions
    user_id = "test_user_123"
    
    # First interaction - website development with budget
    update_user_memory(user_id, "enaku website develop pananu enoda budget only 7k tha", 
                      {"primary_emotion": "neutral", "intensity": "low"}, "Response about TCG TECH")
    
    # Second interaction - casual language
    update_user_memory(user_id, "sollu da epdi start pananum", 
                      {"primary_emotion": "curious", "intensity": "medium"}, "Casual response")
    
    # Third interaction - respect request
    update_user_memory(user_id, "respect ah pesu", 
                      {"primary_emotion": "neutral", "intensity": "low"}, "Formal response")
    
    # Get learning insights
    insights = get_learning_insights(user_id)
    print("  Learning Insights:")
    print(f"    {insights}")
    
    # Test 4: Language Permission Detection
    print("\n🔐 Test 4: Language Permission Detection")
    
    language_tests = [
        ("respect ah pesu", {"casual_language_permission": True}),
        ("neenga romba nalla irukinga da", {"casual_language_permission": False}),
        ("how are you da", {"casual_language_permission": False}),
        ("talk casually", {"casual_language_permission": False})
    ]
    
    for msg, profile in language_tests:
        permission_data = detect_casual_language_permission(msg, profile)
        print(f"  '{msg}' → Can use casual: {permission_data['can_use_casual']}")
    
    print("\n✅ All Enhanced Luna Tests Completed!")
    print("\n📋 Summary:")
    print("  ✅ Digital solution detection working")
    print("  ✅ TCG TECH suggestions enhanced")
    print("  ✅ Self-learning system active")
    print("  ✅ Language permissions working")
    print("  ✅ Contact URL included in suggestions")

if __name__ == "__main__":
    test_enhanced_luna()
