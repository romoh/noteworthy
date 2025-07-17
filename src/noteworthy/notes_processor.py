# noteworthy/notes_processor.py

import os
import json
from typing import List, Optional, TypedDict, Dict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate


class ReleaseNotesState(TypedDict):
    commits: List[str]
    classified_commits: Dict[str, List[str]]
    release_notes: str


def get_classification_prompt() -> ChatPromptTemplate:
    system_prompt = """You are a commit classifier. Classify each commit into one of these categories:
- Feature
- BugFix
- Enhancement
- Docs (optional)
- Other

Respond using JSON format like:
{{"Feature": [...], "BugFix": [...], "Enhancement": [...], "Docs": [...], "Other": [...]}}

"""
    messages = [("system", system_prompt), ("human", "Commits:\n{commits}")]
    return ChatPromptTemplate.from_messages(messages)


def get_summary_prompt(style_sample: Optional[str] = None) -> ChatPromptTemplate:
    system = """You are a release notes generator. Summarize the following list of commits into a concise section.
Use Markdown headers and bullets, and remove repetitive or unimportant details or infrastructure and pipelines changes."""
    messages = [("system", system)]
    if style_sample:
        messages.append(("human", f"Sample style:\n\n{style_sample}"))
    messages.append(("human", "Commits:\n{commits}"))
    return ChatPromptTemplate.from_messages(messages)


def make_classification_node(llm, prompt):
    def classify(state):
        commits_text = "\n".join(state["commits"])
        messages = prompt.format_messages(commits=commits_text)
        response = llm.invoke(messages)
        try:
            classified = json.loads(response.content)
        except json.JSONDecodeError:
            print("❌ Failed to parse classification JSON. Output:\n", response.content)
            # Fallback: put all commits as Features
            classified = {"Feature": state["commits"], "BugFix": [], "Enhancement": [], "Docs": [], "Other": []}
        return {"classified_commits": classified, "commits": state["commits"]}
    return classify


def make_summarize_node(llm, prompt, style_sample):
    category_titles = {
        "Feature": "🚀 Features",
        "BugFix": "🐛 Bug Fixes",
        "Enhancement": "🛠 Enhancements",
        "Docs": "📚 Documentation",
    }

    def summarize(state):
        output_sections = []
        classified = state.get("classified_commits", {})
        for category, commits in classified.items():
            if not commits or category == "Other":
                continue
            messages = prompt.format_messages(commits="\n".join(commits))
            response = llm.invoke(messages)
            header = category_titles.get(category, category)
            section = f"### {header}\n\n{response.content.strip()}"
            output_sections.append(section)
        return {"release_notes": "\n\n".join(output_sections)}

    return summarize


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

    classification_prompt = get_classification_prompt()
    summary_prompt = get_summary_prompt(style_sample=style_text)

    workflow = StateGraph(ReleaseNotesState)

    classification_node = make_classification_node(llm, classification_prompt)
    summarize_node = make_summarize_node(llm, summary_prompt, style_text)

    workflow.add_node("classify", classification_node)
    workflow.add_node("summarize", summarize_node)

    workflow.set_entry_point("classify")
    workflow.add_edge("classify", "summarize")
    workflow.add_edge("summarize", END)
    workflow.set_finish_point("summarize")

    graph = workflow.compile()
    initial_state = ReleaseNotesState(commits=commits, classified_commits={}, release_notes="")
    result = graph.invoke(initial_state)

    return result["release_notes"]
