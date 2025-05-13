from pydantic import BaseModel, Field
from pydantic_ai import Agent

from askademic.constants import GEMINI_2_FLASH_MODEL_ID
from askademic.prompts.general import SYSTEM_PROMPT_ALLOWER_TEMPLATE


class AllowResponse(BaseModel):
    is_scientific: bool = Field(
        description="Whether the question/request is scientific or not."
    )
    pun: str = Field(
        description="""A pun about how the question/request is not scientific.
        Generate this only when is_scientific is False."""
    )


allower_agent = Agent(
    GEMINI_2_FLASH_MODEL_ID,
    system_prompt=SYSTEM_PROMPT_ALLOWER_TEMPLATE,
    output_type=AllowResponse,
    model_settings={"max_tokens": 1000, "temperature": 0},
)
