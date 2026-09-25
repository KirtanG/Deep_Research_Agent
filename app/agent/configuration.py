import os
from typing import Any

from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field


class Configuration(BaseModel):
    """The configuration for the agent."""

    query_generator_model: str = Field(
        default="gemini-3.5-flash-lite",
        description="The name of the language model to use for the agent's query generation.",
    )

    reflection_model: str = Field(
        default="gemini-3.5-flash",
        description="The name of the language model to use for the agent's reflection."
    )

    answer_model: str = Field(
        default="gemini-3.8-flash",
        description="The name of the language model to use for the agent's answer."
    )

    number_of_initial_queries: int = Field(
        default=1,
        description="The number of initial search queries to generate.",
    )

    max_research_loops: int = Field(
        default=1 ,
        description = "The maximum number of research loops to perform.",
    )

    @classmethod
    def from_runnable_config(
        cls, config: RunnableConfig | None = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {  # pyright: ignore[reportExplicitAny]
            name: os.environ.get(name.upper(), configurable.get(name))
            for name in cls.model_fields
        }

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None} # pyright: ignore[reportAny]

        return cls(**values) # pyright: ignore[reportAny]
