#!/usr/bin/env python3
"""
Test script for Luna's language permission system
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import detect_casual_language_permission, detect_techtech_query, detect_emotion

def test_casual_language_detection():
    """Test casual language permission detection"""
    
    print("🧪 Testing Casual Language Permission System")
    print("=" * 50)
    
    test_cases = [
        {
            "message": "respect ah pesu",
            "user_profile": {"casual_language_permission": True},
            "expected": "respect_demanded"
        },
        {
            "message": "neenga romba nalla irukinga da",
            "user_profile": {"casual_language_permission": False},
            "expected": "permission_granted"
        },
        {
            "message": "how are you da",
            "user_profile": {"casual_language_permission": False},
            "expected": "user_uses_casual"
        },
        {
            "message": "tell me about your company",
            "user_profile": {"casual_language_permission": False},
            "expected": "formal"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['message']}")
        result = detect_casual_language_permission(test['message'], test['user_profile'])
        
        print(f"  Permission granted: {result['permission_granted']}")
        print(f"  Respect demanded: {result['respect_demanded']}")
        print(f"  User uses casual: {result['user_uses_casual']}")
        print(f"  Can use casual: {result['can_use_casual']}")
        print(f"  New permission: {result['new_permission']}")

def test_techtech_detection():
    """Test TCG TECH query detection"""
    
    print("\n🏢 Testing TCG TECH Query Detection")
    print("=" * 50)
    
    test_cases = [
        "who created you",
        "about tcg tech",
        "tell me about your company",
        "what is tcgtech",
        "how are you today"
    ]
    
    for i, message in enumerate(test_cases, 1):
        result = detect_techtech_query(message)
        print(f"{i}. '{message}' -> TCG TECH query: {result}")

def test_emotion_detection():
    """Test emotion detection"""
    
    print("\n😊 Testing Emotion Detection")
    print("=" * 50)
    
    test_cases = [
        "I am so happy today!!!",
        "This is making me angry",
        "I feel sad about this",
        "I don't understand what you mean??",
        "tell me more about this"
    ]
    
    for i, message in enumerate(test_cases, 1):
        result = detect_emotion(message)
        print(f"{i}. '{message}'")
        print(f"   Primary emotion: {result['primary_emotion']}")
        print(f"   Intensity: {result['intensity']}")
        print(f"   All emotions: {result['all_emotions']}")

if __name__ == "__main__":
    test_casual_language_detection()
    test_techtech_detection()
    test_emotion_detection()
    
    print("\n✅ All tests completed!")
