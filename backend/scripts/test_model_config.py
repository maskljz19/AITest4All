"""Test Model Configuration and Prompt Management"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings
from app.services.prompt_manager import prompt_manager
from app.agents.factory import create_requirement_agent


async def test_model_config():
    """Test model configuration"""
    print("=" * 60)
    print("Testing Model Configuration")
    print("=" * 60)
    
    print("\n1. Default Model Configuration:")
    print(f"   Provider: {settings.default_model_provider}")
    print(f"   Model: {settings.default_model_name}")
    print(f"   Temperature: {settings.default_temperature}")
    print(f"   Max Tokens: {settings.default_max_tokens}")
    
    print("\n2. API Endpoints:")
    print(f"   OpenAI: {settings.openai_api_base}")
    print(f"   Anthropic: {settings.anthropic_api_base}")
    
    print("\n3. Agent-Specific Models:")
    print(f"   Requirement: {settings.requirement_agent_model or 'Using default'}")
    print(f"   Scenario: {settings.scenario_agent_model or 'Using default'}")
    print(f"   Case: {settings.case_agent_model or 'Using default'}")
    print(f"   Code: {settings.code_agent_model or 'Using default'}")
    print(f"   Quality: {settings.quality_agent_model or 'Using default'}")
    print(f"   Optimize: {settings.optimize_agent_model or 'Using default'}")


async def test_prompt_management():
    """Test prompt management"""
    print("\n" + "=" * 60)
    print("Testing Prompt Management")
    print("=" * 60)
    
    print("\n1. Available Prompts:")
    prompts = prompt_manager.list_prompts()
    for agent_type in prompts.keys():
        print(f"   - {agent_type}")
    
    print("\n2. Sample Prompt (Requirement Agent):")
    req_prompt = prompt_manager.get_prompt("requirement_agent")
    if req_prompt:
        lines = req_prompt.split('\n')
        print(f"   First 5 lines:")
        for line in lines[:5]:
            print(f"   {line}")
        print(f"   ... (total {len(lines)} lines)")
    
    print("\n3. Test Prompt Update:")
    test_prompt = "This is a test prompt for requirement agent."
    success = prompt_manager.set_prompt("test_agent", test_prompt)
    print(f"   Update success: {success}")
    
    retrieved = prompt_manager.get_prompt("test_agent")
    print(f"   Retrieved matches: {retrieved == test_prompt}")


async def test_agent_factory():
    """Test agent factory"""
    print("\n" + "=" * 60)
    print("Testing Agent Factory")
    print("=" * 60)
    
    try:
        print("\n1. Creating Requirement Agent with default config:")
        agent = create_requirement_agent()
        print(f"   Agent Type: {agent.agent_type}")
        print(f"   Model Provider: {agent.model_provider}")
        print(f"   Model Name: {agent.model_name}")
        print(f"   Temperature: {agent.temperature}")
        print(f"   Max Tokens: {agent.max_tokens}")
        print(f"   System Prompt: {'Loaded' if agent.system_prompt else 'Not loaded'}")
        
        print("\n2. Creating Agent with custom config:")
        from app.agents.factory import create_agent
        custom_agent = create_agent(
            agent_type="scenario",
            model_name="gpt-3.5-turbo",
            temperature=0.8,
            max_tokens=1500
        )
        print(f"   Agent Type: {custom_agent.agent_type}")
        print(f"   Model Name: {custom_agent.model_name}")
        print(f"   Temperature: {custom_agent.temperature}")
        print(f"   Max Tokens: {custom_agent.max_tokens}")
        
        print("\n✓ Agent Factory Test Passed")
        
    except Exception as e:
        print(f"\n✗ Agent Factory Test Failed: {str(e)}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("Model Configuration and Prompt Management Test Suite")
    print("=" * 60)
    
    try:
        await test_model_config()
        await test_prompt_management()
        await test_agent_factory()
        
        print("\n" + "=" * 60)
        print("All Tests Completed Successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
