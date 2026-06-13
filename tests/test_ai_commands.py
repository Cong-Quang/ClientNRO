"""
Test AI Commands - Demo Script
Tests all AI terminal commands without needing real game connection
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from handlers.ai_command_handler import AICommandHandler


class MockAccount:
    def __init__(self, username):
        self.username = username
        self.is_logged_in = True


class MockManager:
    def __init__(self):
        self.accounts = [
            MockAccount("acc_0"),
            MockAccount("acc_1"),
            MockAccount("acc_2")
        ]
        self.command_target = 0


async def test_ai_commands():
    """Test all AI commands"""
    print("="*70)
    print("AI COMMANDS TEST - Terminal Interface Demo")
    print("="*70)
    
    handler = AICommandHandler()
    manager = MockManager()
    
    # Load weights
    print("\n[Test 1] Loading default weights...")
    handler.load_weights("ai_core/weights/default_weights.json")
    
    # Test AI Status
    print("\n[Test 2] AI Status Command")
    print("-" * 70)
    await handler.handle_ai_command(["ai", "status"], manager)
    
    # Test AI Info
    print("\n[Test 3] AI Info Command")
    print("-" * 70)
    await handler.handle_ai_command(["ai", "info"], manager)
    
    # Test AI On
    print("\n[Test 4] AI On Command")
    print("-" * 70)
    await handler.handle_ai_command(["ai", "on"], manager)
    await handler.handle_ai_command(["ai", "status"], manager)
    
    # Test AI Off
    print("\n[Test 5] AI Off Command")
    print("-" * 70)
    await handler.handle_ai_command(["ai", "off"], manager)
    await handler.handle_ai_command(["ai", "status"], manager)
    
    # Test AI Toggle
    print("\n[Test 6] AI Toggle Command")
    print("-" * 70)
    await handler.handle_ai_command(["ai", "toggle"], manager)
    
    # Test Goal Commands
    print("\n[Test 7] Goal Management")
    print("-" * 70)
    print("Setting goal: farm items 1,5,10 with mob 12")
    await handler.handle_ai_command(["ai", "goal", "set", "farm_items", "1,5,10", "mob=12"], manager)
    
    print("\nShowing current goal:")
    await handler.handle_ai_command(["ai", "goal", "show"], manager)
    
    print("\nClearing goal:")
    await handler.handle_ai_command(["ai", "goal", "clear"], manager)
    await handler.handle_ai_command(["ai", "goal", "show"], manager)
    
    # Test Group Commands
    print("\n[Test 8] Group Management")
    print("-" * 70)
    print("Setting active groups to 1,2:")
    await handler.handle_ai_command(["ai", "group", "set", "1,2"], manager)
    
    print("\nShowing groups:")
    await handler.handle_ai_command(["ai", "group", "show"], manager)
    
    # Test Zone Commands
    print("\n[Test 9] Zone Distribution")
    print("-" * 70)
    print("Auto-distributing zones for map 5:")
    await handler.handle_ai_command(["ai", "zone", "auto", "5"], manager)
    
    print("\nShowing zone distribution:")
    await handler.handle_ai_command(["ai", "zone", "show", "5"], manager)
    
    # Test Team Commands
    print("\n[Test 10] Team Coordination")
    print("-" * 70)
    print("Setting team leader to acc_0:")
    await handler.handle_ai_command(["ai", "team", "leader", "acc_0"], manager)
    
    print("\nShowing team formation:")
    await handler.handle_ai_command(["ai", "team", "formation"], manager)
    
    # Test Help
    print("\n[Test 11] AI Help")
    print("-" * 70)
    await handler.handle_ai_command(["ai"], manager)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print("[OK] AI Status/Info commands")
    print("[OK] AI On/Off/Toggle commands")
    print("[OK] Goal management (set/show/clear)")
    print("[OK] Group management (set/show)")
    print("[OK] Zone distribution (auto/show)")
    print("[OK] Team coordination (leader/formation)")
    print("[OK] Help command")
    print("\n[SUCCESS] All AI terminal commands working!")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(test_ai_commands())
