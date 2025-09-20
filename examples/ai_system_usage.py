"""
AI Model Management System - Usage Examples
Demonstrates how to use the integrated AI system with multiple models,
load balancing, caching, and performance monitoring.
"""

import asyncio
import json
from typing import Dict, List, Any
import time

# Add parent directory to path
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai.integration import ai_system, ai_complete, ai_embed, ai_metrics, ai_health


async def example_basic_completion():
    """Basic completion example with automatic model selection"""
    print("\n=== Basic Completion Example ===")

    response = await ai_complete(
        prompt="Explain quantum computing in simple terms",
        max_tokens=200,
        temperature=0.7
    )

    print(f"Model used: {response.get('model')}")
    print(f"Response: {response.get('content')[:200]}...")
    print(f"Tokens: {response.get('usage', {})}")
    print(f"Cost: ${response.get('cost', 0):.6f}")


async def example_chat_completion():
    """Chat completion with conversation history"""
    print("\n=== Chat Completion Example ===")

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant specializing in technology."},
        {"role": "user", "content": "What are the latest trends in AI?"},
        {"role": "assistant", "content": "The latest AI trends include..."},
        {"role": "user", "content": "Tell me more about multimodal models"}
    ]

    response = await ai_complete(
        messages=messages,
        model_id="gpt-4o",  # Specific model selection
        max_tokens=300,
        temperature=0.8
    )

    print(f"Response: {response.get('content')[:300]}...")


async def example_with_caching():
    """Demonstrate caching behavior"""
    print("\n=== Caching Example ===")

    prompt = "What are the benefits of using Python for data science?"

    # First request - will hit the model
    start = time.time()
    response1 = await ai_complete(
        prompt=prompt,
        max_tokens=150,
        use_cache=True
    )
    time1 = time.time() - start
    print(f"First request: {time1:.2f}s (cache miss)")

    # Second request - should hit cache
    start = time.time()
    response2 = await ai_complete(
        prompt=prompt,
        max_tokens=150,
        use_cache=True
    )
    time2 = time.time() - start
    print(f"Second request: {time2:.2f}s (cache hit)")
    print(f"Speed improvement: {time1/time2:.1f}x faster")


async def example_semantic_caching():
    """Demonstrate semantic caching with similar queries"""
    print("\n=== Semantic Caching Example ===")

    # First query
    query1 = "What are the advantages of machine learning?"
    response1 = await ai_complete(
        prompt=query1,
        use_cache=True,
        use_semantic_cache=True
    )
    print(f"Query 1: {query1}")
    print(f"Response 1: {response1.get('content')[:100]}...")

    # Similar query - should hit semantic cache
    query2 = "What are the benefits of ML algorithms?"
    start = time.time()
    response2 = await ai_complete(
        prompt=query2,
        use_cache=True,
        use_semantic_cache=True
    )
    elapsed = time.time() - start
    print(f"\nQuery 2 (similar): {query2}")
    print(f"Response time: {elapsed:.3f}s")
    print(f"Semantic cache hit: {elapsed < 0.1}")


async def example_parallel_requests():
    """Demonstrate load balancing with parallel requests"""
    print("\n=== Parallel Requests with Load Balancing ===")

    prompts = [
        "Explain neural networks",
        "What is deep learning?",
        "Describe transformer architecture",
        "What are embeddings?",
        "Explain attention mechanism"
    ]

    # Send parallel requests
    start = time.time()
    tasks = [
        ai_complete(prompt=p, max_tokens=100)
        for p in prompts
    ]
    responses = await asyncio.gather(*tasks)
    elapsed = time.time() - start

    # Analyze model distribution
    model_usage = {}
    for r in responses:
        model = r.get("model", "unknown")
        model_usage[model] = model_usage.get(model, 0) + 1

    print(f"Completed {len(prompts)} requests in {elapsed:.2f}s")
    print(f"Model distribution: {model_usage}")


async def example_cost_optimized_routing():
    """Demonstrate cost-optimized model selection"""
    print("\n=== Cost-Optimized Routing Example ===")

    # Initialize with cost optimization
    await ai_system.initialize()

    # Simple query - should route to cheaper model
    simple_response = await ai_complete(
        prompt="What is 2+2?",
        max_tokens=10,
        model_selection_strategy="cost_optimized"
    )
    print(f"Simple query model: {simple_response.get('model')}")
    print(f"Cost: ${simple_response.get('cost', 0):.6f}")

    # Complex query - might use more capable model
    complex_response = await ai_complete(
        prompt="Analyze the philosophical implications of consciousness in artificial intelligence",
        max_tokens=500,
        model_selection_strategy="weighted"
    )
    print(f"Complex query model: {complex_response.get('model')}")
    print(f"Cost: ${complex_response.get('cost', 0):.6f}")


async def example_function_calling():
    """Demonstrate function calling with compatible models"""
    print("\n=== Function Calling Example ===")

    functions = [
        {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "units": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    ]

    response = await ai_complete(
        prompt="What's the weather like in San Francisco?",
        functions=functions,
        model_selection_strategy="function_calling_routing"
    )

    print(f"Model used: {response.get('model')}")
    print(f"Function call: {response.get('function_call', 'No function called')}")


async def example_streaming_response():
    """Demonstrate streaming responses"""
    print("\n=== Streaming Response Example ===")

    # Note: Actual streaming implementation would yield chunks
    response = await ai_complete(
        prompt="Write a short story about AI",
        max_tokens=200,
        stream=True
    )

    print(f"Streaming enabled with model: {response.get('model')}")
    print("(Full streaming implementation would yield chunks in real-time)")


async def example_embedding_generation():
    """Generate and cache embeddings"""
    print("\n=== Embedding Generation Example ===")

    texts = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks with multiple layers",
        "Natural language processing helps computers understand text"
    ]

    embeddings = []
    for text in texts:
        embedding = await ai_embed(text)
        embeddings.append(embedding[:5])  # Show first 5 dimensions
        print(f"Text: {text[:50]}...")
        print(f"Embedding (first 5 dims): {embedding[:5]}")

    # Calculate similarity
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np

    if len(embeddings) > 1:
        sim_matrix = cosine_similarity(embeddings)
        print(f"\nSimilarity between text 0 and 1: {sim_matrix[0][1]:.3f}")


async def example_performance_metrics():
    """Display performance metrics and monitoring"""
    print("\n=== Performance Metrics Example ===")

    # Get metrics for all models
    metrics = await ai_metrics(time_range="1h")

    for model_id, model_metrics in metrics.items():
        if not model_metrics.get("no_data"):
            print(f"\nModel: {model_id}")
            print(f"  Total requests: {model_metrics.get('total_requests', 0)}")
            print(f"  Success rate: {model_metrics.get('success_rate', 0):.1f}%")
            print(f"  Cache hit rate: {model_metrics.get('cache_hit_rate', 0):.1f}%")
            print(f"  Avg latency: {model_metrics.get('latency', {}).get('avg', 0):.0f}ms")
            print(f"  Total cost: ${model_metrics.get('cost', {}).get('total', 0):.4f}")


async def example_health_monitoring():
    """Monitor model health scores"""
    print("\n=== Health Monitoring Example ===")

    health_scores = await ai_health()

    for model_id, score in health_scores.items():
        status = "🟢" if score > 80 else "🟡" if score > 50 else "🔴"
        print(f"{status} {model_id}: {score:.1f}/100")


async def example_cache_management():
    """Demonstrate cache invalidation and management"""
    print("\n=== Cache Management Example ===")

    # Add some items to cache
    await ai_complete(prompt="Test query 1", use_cache=True)
    await ai_complete(prompt="Test query 2", use_cache=True)

    # Get cache stats
    cache_stats = ai_system.cache_manager.get_stats()
    print(f"Cache stats: {cache_stats}")

    # Invalidate specific pattern
    await ai_system.invalidate_cache(pattern="Test*")
    print("Cache invalidated for pattern 'Test*'")


async def example_error_handling():
    """Demonstrate error handling and fallback"""
    print("\n=== Error Handling Example ===")

    try:
        # Try with an invalid model
        response = await ai_complete(
            prompt="Test prompt",
            model_id="non-existent-model"
        )
    except Exception as e:
        print(f"Error caught: {e}")

    # System will automatically fallback to available model
    response = await ai_complete(
        prompt="Test prompt with automatic fallback",
        max_tokens=50
    )
    print(f"Fallback succeeded with model: {response.get('model')}")


async def run_all_examples():
    """Run all examples"""
    # Initialize the AI system
    await ai_system.initialize()

    examples = [
        example_basic_completion,
        example_chat_completion,
        example_with_caching,
        example_semantic_caching,
        example_parallel_requests,
        example_cost_optimized_routing,
        example_function_calling,
        example_streaming_response,
        example_embedding_generation,
        example_performance_metrics,
        example_health_monitoring,
        example_cache_management,
        example_error_handling
    ]

    for example in examples:
        try:
            await example()
            await asyncio.sleep(1)  # Small delay between examples
        except Exception as e:
            print(f"Example {example.__name__} failed: {e}")

    # Cleanup
    await ai_system.shutdown()


if __name__ == "__main__":
    print("=== AI Model Management System - Examples ===")
    print("This demonstrates various features of the AI system:")
    print("- Multiple model support (OpenAI, Anthropic, Ollama)")
    print("- Intelligent load balancing")
    print("- Response caching (exact and semantic)")
    print("- Performance monitoring")
    print("- Cost optimization")
    print("- Error handling and fallbacks")

    # Run examples
    asyncio.run(run_all_examples())