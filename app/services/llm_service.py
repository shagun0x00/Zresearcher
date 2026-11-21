# Handles all our communication with OpenRouter / LLM APIs.
import json

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class LLMServiceError(Exception):
    """Custom exception we raise whenever the LLM flakes out or returns garbage."""


class LLMService:
    """Wrapper around the OpenAI client configured for OpenRouter endpoints."""

    def __init__(self):
        # Fire up the OpenAI SDK pointing to OpenRouter's base URL
        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            max_retries=2,
        )

        self.model = OPENROUTER_MODEL

    def generate_response(self, prompt: str) -> str:
        """Send a standard text prompt and get back a raw string response."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=0.2, # Keep things relatively deterministic
            )

            content = response.choices[0].message.content

            # Sometimes models return empty content even on 200 OK, guard against that
            if not content:
                raise LLMServiceError(
                    "The model returned an empty response."
                )

            return content

        except LLMServiceError:
            raise

        except Exception as exc:
            raise LLMServiceError(
                f"LLM request failed: {exc}"
            ) from exc

    def generate_structured_response(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Force the model to return JSON matching a specific Pydantic schema."""

        # Craft a strict system-like instruction asking for exact JSON format
        structured_prompt = f"""
{prompt}

Return only valid JSON.
Do not include markdown code fences.

Your response must follow this JSON schema:

{json.dumps(schema.model_json_schema(), indent=2)}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": structured_prompt,
                    }
                ],
                temperature=0.1, # Extra low temp so it doesn't get creative with keys
                response_format={
                    "type": "json_object"
                },
            )

            content = response.choices[0].message.content

            if not content:
                raise LLMServiceError(
                    "The model returned an empty JSON response."
                )

            # Parse raw JSON string into a dict
            data = json.loads(content)

            # Validate and instantiate our Pydantic model
            return schema.model_validate(data)

        except (json.JSONDecodeError, ValidationError) as exc:
            raise LLMServiceError(
                f"Invalid structured response: {exc}"
            ) from exc

        except LLMServiceError:
            raise

        except Exception as exc:
            raise LLMServiceError(
                f"Structured generation failed: {exc}"
            ) from exc


# Shared service instance
llm_service = LLMService()
