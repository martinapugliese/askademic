from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_evals import Dataset

from askademic.question import QuestionAnswerResponse, question_agent


class Request(BaseModel):
    request: str = Field(description="The request to the agent")


questions_file = Path("questions_dataset.yaml")
questions_dataset = Dataset[Request, QuestionAnswerResponse, dict].from_file(
    questions_file
)

print(f"Loaded dataset with {len(questions_dataset.cases)} cases")


# import asyncio
# import nest_asyncio
# nest_asyncio.apply()

# def make_request_sync(request: Request) -> QuestionAnswerResponse:
#     print(f"Evaluating request: {request}")
#     loop = asyncio.get_event_loop()
#     return loop.run_until_complete(make_request(request))


async def make_request(request: Request) -> QuestionAnswerResponse:
    try:
        print(f"Processing request: {request.request}")
        r = await question_agent.run(request.request)
        print(f"AgentRunResult: {r}")  # Debugging the entire result object
        print(f"Attributes of AgentRunResult: {dir(r)}")

        # Forcefully set trace_id as an integer
        try:
            r.trace_id = 0  # Ensure trace_id is always an integer
        except AttributeError:
            object.__setattr__(
                r, "trace_id", 0
            )  # Use setattr if direct assignment fails

        # Debugging: Format the trace_id for printing only
        formatted_trace_id = f"{r.trace_id:032x}"
        print(f"Formatted Trace ID: {formatted_trace_id}")

        if not isinstance(r.output, QuestionAnswerResponse):
            raise AssertionError(
                f"Expected QuestionAnswerResponse, but got: {type(r.output)}"
            )
        return r.output
    except Exception as e:
        print(f"Error in make_request: {e}")
        raise


questions_dataset.evaluate_sync(make_request)

questions_dataset.evaluate_sync(make_request)

questions_dataset.evaluate_sync(make_request)

questions_dataset.evaluate_sync(make_request)
