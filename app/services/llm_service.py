
# app/services/llm_service.py

import json
import time

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from app.config import OPENROUTER_API_KEY, OPENROUTER_MODEL


class LLMServiceError(Exception):
    """Raised when the LLM request fails or returns invalid output."""


class LLMService:

    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is missing from .env")

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1",
            timeout=60.0,
            max_retries=2,
        )

        self.model = OPENROUTER_MODEL
        self.max_attempts = 3

    def _extract_content(self, response) -> str:
        """Safely extract text from an OpenAI-compatible response."""

        if not response or not response.choices:
            raise LLMServiceError("The model returned no response choices.")

        message = response.choices[0].message
        content = message.content

        if not content or not content.strip():
            finish_reason = response.choices[0].finish_reason
            raise LLMServiceError(
                f"The model returned empty content. Finish reason: {finish_reason}"
            )

        return content.strip()

    def generate_response(self, prompt: str) -> str:
        """Generate a normal text response with retry handling."""

        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.2,
                )

                return self._extract_content(response)

            except Exception as exc:
                last_error = exc

                if attempt < self.max_attempts:
                    time.sleep(attempt * 2)

        raise LLMServiceError(
            f"LLM request failed after {self.max_attempts} attempts: {last_error}"
        ) from last_error

    def generate_structured_response(
        self,
        prompt: str,
        schema: type[BaseModel],
    ) -> BaseModel:
        """Generate and validate a structured Pydantic response."""

        structured_prompt = f"""
You are a structured data generation system.

Follow the instructions and return one valid JSON object.

Rules:
- Return JSON only.
- Do not use Markdown code fences.
- Do not add explanations outside the JSON.
- Include every required field.
- Use the correct data types.
- Do not invent unsupported information.
- If a list has no items, return an empty list.

Required JSON schema:

{json.dumps(schema.model_json_schema(), indent=2)}

TASK:

{prompt}
"""

        last_error = None

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": structured_prompt,
                        }
                    ],
                    temperature=0.1,
                    response_format={"type": "json_object"},
                )

                content = self._extract_content(response)

                # Remove accidental Markdown code fences.
                if content.startswith("```"):
                    content = content.replace("```json", "", 1)
                    content = content.replace("```", "").strip()

                data = json.loads(content)

                return schema.model_validate(data)

            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc

            except Exception as exc:
                last_error = exc

            if attempt < self.max_attempts:
                time.sleep(attempt * 2)

        raise LLMServiceError(
            f"Structured generation failed after "
            f"{self.max_attempts} attempts: {last_error}"
        ) from last_error


# Shared service instance
llm_service = LLMService()
