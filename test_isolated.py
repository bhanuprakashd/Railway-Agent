"""Test each query in complete isolation."""

import asyncio
import sys

async def test_isolated_query(query):
    """Test a single query in complete isolation."""
    # Import inside function to get fresh instances
    from train_agent.agent import workflow, reset_session
    
    # Reset before test
    await reset_session()
    
    # Run query
    response = await workflow(query)
    
    return response


async def main():
    tests = [
        ('Train Search', 'Show me trains from Hyderabad to Bangalore'),
        ('Station Code', 'What is the station code for Chennai?'),
    ]
    
    for name, query in tests:
        print(f'\n{"="*70}')
        print(f'🧪 {name}: {query}')
        print("="*70)
        
        response = await test_isolated_query(query)
        
        is_tool_call = 'Tool Calls:' in response
        print(f'\nStatus: {"❌ TOOL CALL" if is_tool_call else "✅ NATURAL"}')
        print(f'Preview: {response[:250]}...\n')
        
        await asyncio.sleep(3)


if __name__ == "__main__":
    asyncio.run(main())

