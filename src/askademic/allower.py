from pydantic import BaseModel, Field
from pydantic_ai import Agent

from askademic.prompts.general import SYSTEM_PROMPT_ALLOWER


class AllowResponse(BaseModel):
    is_scientific: bool = Field(
        description="Whether the question/request is scientific or not."
    )
    pun: str = Field(
        description="""A pun about how the question/request is not scientific.
        Generate this only when is_scientific is False."""
    )


allower_agent_base = Agent(
    system_prompt=SYSTEM_PROMPT_ALLOWER,
    output_type=AllowResponse,
    model_settings={"max_tokens": 1000, "temperature": 0},
)
