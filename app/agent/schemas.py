from datetime import datetime

from pydantic import BaseModel, Field


class SearchQueryList(BaseModel):
    query: list[str] = Field(
        description="A list of search queries to be used for web research."
    )
    rationale: str = Field(
        description="A brief explanation of why these queries are relevant to the research topic."
    )


class Reflection(BaseModel):
    is_sufficient: bool = Field(
        description="Whether the provided summaries are sufficient to answer the user's question."
    )
    knowledge_gap: str = Field(
        description="A description of what information is missing or needs clarification."
    )
    follow_up_queries: list[str] = Field(
        description="A list of follow-up queries to address the knowledge gap."
    )

class SearchResults(BaseModel):
    url: str = Field(
        description="The url of the Search Result."
    )

    content: str | None = Field(
        description="The page contents of the url",
        default=None
    )

    title: str | None = Field(
        description="Title of the url",
        default = None
    )

    published_date:  datetime | None = Field(
        description="Published Date of the url",
        default=None
    )