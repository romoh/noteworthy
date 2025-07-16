# noteworthy/notes_processor.py

import os
from typing import List, Optional, TypedDict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate


class ReleaseNotesState(TypedDict):
    commits: List[str]
    release_notes: str

def get_prompt(style_sample: Optional[str] = None):
    system_prompt = """You are a release notes generator. Given a list of commit messages and the number of files changed for each, group them into sections such as Features, Bug Fixes, etc.
At the top, start with the features sorted by the most impactful changes.
Correlate related changes, especially small implementation details and fixes, into meaningful groups rather than listing them separately.
Output in a concise, non-verbose style, using clear section headers. Avoid repeating information, remove title prefix and keep lists short and to the point.
Output in Markdown format."""

    messages = [("system", system_prompt)]

    if style_sample:
        messages.append(("human", f"Here is a sample release note for stylistic guidance:\n\n{style_sample}"))

    messages.append(("human", "Commits:\n{commits}"))

    return ChatPromptTemplate.from_messages(messages)


def make_summarize_node(llm, prompt):
    def summarize_node(state):
        commit_text = "\n".join(state["commits"])
        messages = prompt.format_messages(commits=commit_text)
        response = llm.invoke(messages)
        return {"release_notes": response.content}
    return summarize_node

def process_release_notes(commits: List[str], style_text: Optional[str] = None) -> str:
    deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "test")
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://aiopsvteam.openai.azure.com/")
    openai_api_version = os.getenv("OPENAI_API_VERSION", "2024-02-15-preview")

    token_provider = get_bearer_token_provider(
        DefaultAzureCredential(),
        "https://cognitiveservices.azure.com/.default"
    )

    llm = AzureChatOpenAI(
        deployment_name=deployment_name,
        azure_endpoint=azure_endpoint,
        openai_api_version=openai_api_version,
        azure_ad_token_provider=token_provider,
    )

    prompt = get_prompt()
    summarize_node = make_summarize_node(llm, prompt)

    workflow = StateGraph(ReleaseNotesState)
    workflow.add_node("summarize", summarize_node)
    workflow.set_entry_point("summarize")
    workflow.add_edge("summarize", END)
    workflow.set_finish_point("summarize")

    graph = workflow.compile()
    result = graph.invoke({"commits": commits})

    return result["release_notes"]
