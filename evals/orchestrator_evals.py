from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_evals import Dataset

from askademic.orchestrator import SummaryResponse, orchestrator_agent


class Request(BaseModel):
    request: str = Field(description="The request to the agent")


evals_file = Path("orchestrator_dataset.yaml")
evals_dataset = Dataset[Request, SummaryResponse, dict].from_file(evals_file)

print(f"Loaded dataset with {len(evals_dataset.cases)} cases")


async def make_request(request: Request) -> SummaryResponse:
    try:
        print(f"Processing request: {request.request}")
        r = await orchestrator_agent.run(request.request)
        print(f"AgentRunResult: {r}")  # Debugging the entire result object
        print(f"Attributes of AgentRunResult: {dir(r)}")

        # # Forcefully set trace_id as an integer
        # try:
        #     r.trace_id = 0  # Ensure trace_id is always an integer
        # except AttributeError:
        #     object.__setattr__(
        #         r, "trace_id", 0
        #     )  # Use setattr if direct assignment fails

        # # Debugging: Format the trace_id for printing only
        # formatted_trace_id = f"{r.trace_id:032x}"
        # print(f"Formatted Trace ID: {formatted_trace_id}")

        if not isinstance(r.output, SummaryResponse):
            raise AssertionError(
                f"Expected QuestionAnswerResponse, but got: {type(r.output)}"
            )
        return r.output
    except Exception as e:
        print(f"Error in make_request: {e}")
        raise


evals_dataset.evaluate_sync(make_request)
