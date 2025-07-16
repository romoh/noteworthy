# noteworthy/notes_processor.py

import os
from typing import List, TypedDict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

class ReleaseNotesState(TypedDict):
    commits: List[str]
    release_notes: str

def get_prompt():
    return ChatPromptTemplate.from_messages([
        ("system", "You are a release notes generator. Given a list of commit messages, group them into sections such as Features, Bug Fixes, Refactoring, Documentation, etc. Summarize each section in a human-readable way. Output in Markdown format with clear section headers."),
        ("human", "Commits:\n{commits}")
    ])

def make_summarize_node(llm, prompt):
    def summarize_node(state):
        commit_text = "\n".join(state["commits"])
        messages = prompt.format_messages(commits=commit_text)
        response = llm.invoke(messages)
        return {"release_notes": response.content}
    return summarize_node

def process_release_notes(commits: List[str]) -> str:
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
