"""
Claude API client wrapper
Provides interaction with Anthropic Claude API
"""

from anthropic import Anthropic, APIError, RateLimitError as AnthropicRateLimitError
import asyncio
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CreationMetrics:
    """Creation metrics tracking"""
    total_tokens_used: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    api_calls: int = 0
    total_cost: float = 0.0
    success_rate: float = 1.0
    average_response_time: float = 0.0
    errors: List[str] = field(default_factory=list)

    def add_usage(self, input_tokens: int, output_tokens: int, cost: float, response_time: float):
        """Add usage record"""
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens_used += (input_tokens + output_tokens)
        self.api_calls += 1
        self.total_cost += cost

        # Calculate average response time
        if self.api_calls == 1:
            self.average_response_time = response_time
        else:
            self.average_response_time = (
                (self.average_response_time * (self.api_calls - 1) + response_time)
                / self.api_calls
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_tokens_used": self.total_tokens_used,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "api_calls": self.api_calls,
            "total_cost": round(self.total_cost, 4),
            "success_rate": round(self.success_rate, 2),
            "average_response_time": round(self.average_response_time, 2),
            "errors": self.errors
        }


class ClaudeClient:
    """Claude API client wrapper"""

    # Pricing per million tokens
    PRICING = {
        "claude-3-opus-20240229": {
            "input": 15.0,   # $15 per million input tokens
            "output": 75.0   # $75 per million output tokens
        },
        "claude-3-5-sonnet-20240620": {
            "input": 3.0,    # $3 per million input tokens
            "output": 15.0   # $15 per million output tokens
        },
        "claude-3-sonnet-20240229": {
            "input": 3.0,    # $3 per million input tokens
            "output": 15.0   # $15 per million output tokens
        },
        "claude-3-haiku-20240307": {
            "input": 0.25,   # $0.25 per million input tokens
            "output": 1.25   # $1.25 per million output tokens
        }
    }

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key
            model: Model name to use
        """
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key)
        self.metrics = CreationMetrics()
        self.rate_limiter = RateLimiter()

    async def create_content(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 4000,
        temperature: float = 0.8,
        stream: bool = False,
        retry_count: int = 3
    ) -> Dict[str, Any]:
        """
        Call Claude API to generate content

        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            max_tokens: Maximum tokens to generate
            temperature: Temperature parameter (0-1)
            stream: Whether to use streaming response
            retry_count: Number of retries

        Returns:
            Dictionary containing generated content and metrics
        """
        await self.rate_limiter.acquire()

        start_time = datetime.now()
        last_error = None

        for attempt in range(retry_count):
            try:
                logger.info(f"Calling Claude API (attempt {attempt + 1}/{retry_count})")

                # Synchronous call (anthropic library is mainly synchronous)
                response = await asyncio.to_thread(
                    self._call_api,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=stream
                )

                # Calculate cost
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens
                cost = self._calculate_cost(input_tokens, output_tokens)

                # Record metrics
                response_time = (datetime.now() - start_time).total_seconds()
                self.metrics.add_usage(input_tokens, output_tokens, cost, response_time)

                logger.info(f"API call successful: {input_tokens}+{output_tokens} tokens, cost: ${cost:.4f}")

                return {
                    "content": response.content[0].text,
                    "usage": {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    },
                    "cost": cost,
                    "response_time": response_time,
                    "model": self.model,
                    "success": True
                }

            except AnthropicRateLimitError as e:
                last_error = e
                wait_time = min(2 ** attempt * 5, 60)  # Exponential backoff, max 60 seconds
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry: {e}")
                await asyncio.sleep(wait_time)

            except APIError as e:
                last_error = e
                logger.error(f"API error (attempt {attempt + 1}): {e}")
                if attempt < retry_count - 1:
                    await asyncio.sleep(2)

            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error: {e}")
                break

        # Record error
        self.metrics.errors.append(str(last_error))
        self.metrics.success_rate = (
            (self.metrics.api_calls - len(self.metrics.errors)) / self.metrics.api_calls
            if self.metrics.api_calls > 0 else 0
        )

        raise Exception(f"API call failed after {retry_count} retries: {last_error}")

    def _call_api(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        stream: bool
    ):
        """Internal API call method"""
        return self.client.messages.create(
            model=self.model,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream
        )

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """
        Calculate API call cost

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Cost in USD
        """
        pricing = self.PRICING.get(self.model, self.PRICING["claude-3-sonnet-20240229"])

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]

        return round(input_cost + output_cost, 6)

    def get_metrics(self) -> Dict[str, Any]:
        """Get usage metrics"""
        return self.metrics.to_dict()

    def reset_metrics(self):
        """Reset metrics"""
        self.metrics = CreationMetrics()


class RateLimiter:
    """Rate limiter"""

    def __init__(self, max_requests_per_minute: int = 5):
        """
        Initialize rate limiter

        Args:
            max_requests_per_minute: Maximum requests per minute
        """
        self.max_requests = max_requests_per_minute
        self.requests = []
        self.lock = asyncio.Lock()

    async def acquire(self):
        """Acquire request permission"""
        async with self.lock:
            now = datetime.now()

            # Clean up requests older than one minute
            self.requests = [
                req_time for req_time in self.requests
                if now - req_time < timedelta(minutes=1)
            ]

            # Check if exceeding limit
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = min(self.requests)
                wait_time = 60 - (now - oldest_request).total_seconds()

                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.1f} seconds")
                    await asyncio.sleep(wait_time)

                    # Clean up again
                    now = datetime.now()
                    self.requests = [
                        req_time for req_time in self.requests
                        if now - req_time < timedelta(minutes=1)
                    ]

            # Record current request
            self.requests.append(now)