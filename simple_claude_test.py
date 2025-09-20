#!/usr/bin/env python3
"""
Simple Claude API test
"""

import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from claude_client import ClaudeClient
from config import config

async def test_api():
    print("Testing Claude API...")
    print(f"API key configured: {config.has_claude_api_key}")

    if not config.has_claude_api_key:
        print("No API key configured!")
        return False

    client = ClaudeClient(config.claude_api_key, config.claude_model)

    try:
        response = await client.create_content(
            system_prompt="You are a helpful assistant.",
            user_prompt="Write a very short story about a magic system called law chains.",
            max_tokens=200
        )

        print("Success!")
        print(f"Content: {response['content'][:100]}...")
        print(f"Tokens: {response['usage']['total_tokens']}")
        print(f"Cost: ${response['cost']:.4f}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_api())
    print("Test passed!" if result else "Test failed!")