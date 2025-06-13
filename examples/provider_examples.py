#!/usr/bin/env python3
"""
Provider Examples - auto_codex

Demonstrates using different AI providers:
- OpenAI, Azure, Gemini, Ollama, Mistral, etc.
- Provider configuration and validation
- Provider-specific features
"""

import sys
import os

# Add auto_codex to path for examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from auto_codex import CodexRun, CodexSession, SUPPORTED_PROVIDERS, validate_provider_config


def list_supported_providers():
    """List all supported providers"""
    print("Supported Providers Example")
    print("=" * 30)
    
    print("Available providers:")
    for provider, config in SUPPORTED_PROVIDERS.items():
        print(f"  {provider}: {config['name']}")
        print(f"    Base URL: {config['base_url']}")
        print(f"    Env Key: {config['env_key']}")
    
    return SUPPORTED_PROVIDERS


def openai_example():
    """OpenAI provider example"""
    print("\nOpenAI Provider Example")
    print("=" * 30)
    
    try:
        run = CodexRun(
            prompt="Create a simple Python calculator",
            model="gpt-4",
            provider="openai",
            validate_env=False  # Skip validation for demo
        )
        
        print(f"Created OpenAI run: {run.run_id[:8]}...")
        print(f"Provider: {run.provider}")
        print(f"Model: {run.model}")
        
        return run
    except Exception as e:
        print(f"OpenAI setup error: {e}")
        return None


def ollama_example():
    """Ollama (local) provider example"""
    print("\nOllama Provider Example")
    print("=" * 30)
    
    try:
        run = CodexRun(
            prompt="Write a Python function to read CSV files",
            model="llama2",
            provider="ollama",
            validate_env=False  # Skip validation for demo
        )
        
        print(f"Created Ollama run: {run.run_id[:8]}...")
        print(f"Provider: {run.provider}")
        print(f"Model: {run.model}")
        print("Note: Requires Ollama running locally")
        
        return run
    except Exception as e:
        print(f"Ollama setup error: {e}")
        return None


def gemini_example():
    """Gemini provider example"""
    print("\nGemini Provider Example")
    print("=" * 30)
    
    try:
        run = CodexRun(
            prompt="Create a data analysis script",
            model="gemini-pro",
            provider="gemini",
            validate_env=False  # Skip validation for demo
        )
        
        print(f"Created Gemini run: {run.run_id[:8]}...")
        print(f"Provider: {run.provider}")
        print(f"Model: {run.model}")
        
        return run
    except Exception as e:
        print(f"Gemini setup error: {e}")
        return None


def multi_provider_session():
    """Session with multiple providers"""
    print("\nMulti-Provider Session Example")
    print("=" * 30)
    
    session = CodexSession(session_id="multi-provider-demo")
    
    # Different providers for different tasks
    provider_tasks = [
        ("openai", "gpt-4", "Create a web API"),
        ("gemini", "gemini-pro", "Write documentation"),
        ("ollama", "llama2", "Create unit tests")
    ]
    
    runs = []
    for provider, model, task in provider_tasks:
        try:
            run = session.add_run(
                prompt=task,
                model=model,
                provider=provider
            )
            runs.append(run)
            print(f"Added {provider} run: {task}")
        except Exception as e:
            print(f"Failed to add {provider} run: {e}")
    
    print(f"\nSession has {len(session.runs)} runs across {len(set(r.provider for r in session.runs))} providers")
    
    return session


def provider_validation_example():
    """Provider configuration validation"""
    print("\nProvider Validation Example")
    print("=" * 30)
    
    providers_to_test = ["openai", "gemini", "ollama", "invalid_provider"]
    
    for provider in providers_to_test:
        try:
            validate_provider_config(provider)
            print(f"✅ {provider}: Valid configuration")
        except ValueError as e:
            print(f"❌ {provider}: {e}")
        except RuntimeError as e:
            print(f"⚠️  {provider}: {e}")


def provider_comparison_example():
    """Compare different providers for same task"""
    print("\nProvider Comparison Example")
    print("=" * 30)
    
    task = "Write a Python function to calculate prime numbers"
    providers = ["openai", "gemini", "mistral"]
    
    session = CodexSession(session_id="provider-comparison")
    
    runs = []
    for provider in providers:
        try:
            run = session.add_run(
                prompt=task,
                model="gpt-4" if provider == "openai" else "gemini-pro" if provider == "gemini" else "mistral-medium",
                provider=provider
            )
            runs.append(run)
            print(f"Created {provider} run for comparison")
        except Exception as e:
            print(f"Failed to create {provider} run: {e}")
    
    print(f"\nComparison setup complete: {len(runs)} providers")
    print("Execute session to compare results across providers")
    
    return session


def main():
    """Run all provider examples"""
    print("Auto-Codex Provider Examples")
    print("=" * 35)
    
    providers = list_supported_providers()
    openai_run = openai_example()
    ollama_run = ollama_example()
    gemini_run = gemini_example()
    session = multi_provider_session()
    provider_validation_example()
    comparison_session = provider_comparison_example()
    
    print(f"\nProvider examples completed!")
    print(f"Demonstrated {len(providers)} providers")


if __name__ == "__main__":
    main()
