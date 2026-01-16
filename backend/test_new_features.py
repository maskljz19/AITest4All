"""Simple test for new features"""

import sys
from pathlib import Path

print("Testing new features...")
print("=" * 60)

# Test 1: Import config
print("\n1. Testing config imports...")
try:
    from app.core.config import settings
    print(f"   ✓ Config loaded")
    print(f"   - Default provider: {settings.default_model_provider}")
    print(f"   - Default model: {settings.default_model_name}")
    print(f"   - OpenAI base: {settings.openai_api_base}")
    print(f"   - Prompts dir: {settings.agent_prompts_dir}")
except Exception as e:
    print(f"   ✗ Config import failed: {e}")
    sys.exit(1)

# Test 2: Import prompt manager
print("\n2. Testing prompt manager...")
try:
    from app.services.prompt_manager import PromptManager, prompt_manager
    print(f"   ✓ Prompt manager imported")
    print(f"   - Prompts dir: {prompt_manager.prompts_dir}")
except Exception as e:
    print(f"   ✗ Prompt manager import failed: {e}")
    sys.exit(1)

# Test 3: Import agent factory
print("\n3. Testing agent factory...")
try:
    from app.agents.factory import create_agent, get_model_config_for_agent
    print(f"   ✓ Agent factory imported")
    
    provider, model = get_model_config_for_agent("requirement")
    print(f"   - Requirement agent: {provider}/{model}")
except Exception as e:
    print(f"   ✗ Agent factory import failed: {e}")
    sys.exit(1)

# Test 4: Import API modules
print("\n4. Testing API modules...")
try:
    from app.api.prompts import router as prompts_router
    from app.api.model_config import router as model_config_router
    print(f"   ✓ API modules imported")
    print(f"   - Prompts router: {prompts_router.prefix}")
    print(f"   - Model config router: {model_config_router.prefix}")
except Exception as e:
    print(f"   ✗ API modules import failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("All tests passed! ✓")
print("=" * 60)
