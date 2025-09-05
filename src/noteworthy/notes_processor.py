# noteworthy/notes_processor.py

import os
import json
import re
from typing import List, Optional, TypedDict, Dict
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from langgraph.graph import StateGraph, END
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import time
import random
from openai import RateLimitError


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

If a commit message mentions a security fix or CVE, always classify it as a BugFix.

Respond using JSON format like:
{{"Feature": [...], "BugFix": [...], "Enhancement": [...], "Docs": [...], "Other": [...]}}

"""
    messages = [("system", system_prompt), ("human", "Commits:\n{commits}")]
    return ChatPromptTemplate.from_messages(messages)


def get_summary_prompt(style_sample: Optional[str] = None) -> ChatPromptTemplate:
    system = (
        "You are a release notes generator. Summarize the following list of commits for the category '{category}' "
        "as a bullet list, without repeating global headers or section titles. "
        "Imitate the style and level of detail of the provided style sample. "
        "If the style sample includes security details or CVE fixes, do the same. "
        "Do not include 'Release Notes', category headers, or any Markdown headers in your output. "
        "Only provide a bullet list. "
        "Consolidate commits that changes same files and remove infrastructure, pipeline, or github actions changes."
    )
    messages = [("system", system)]
    if style_sample:
        messages.append(("human", f"Sample style:\n\n{style_sample}"))
    messages.append(("human", "Commits:\n{commits}"))
    return ChatPromptTemplate.from_messages(messages)


def extract_json_from_text(text: str) -> str:
    """Extract JSON object from LLM output, stripping code fences and extra text."""
    text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE)
    text = re.sub(r"```$", "", text.strip())
    match = re.search(r'({[\s\S]*})', text)
    if match:
        return match.group(1)
    return text


def make_classification_node(llm, prompt, batch_size: int = 50):
    def classify(state):
        all_classified = {"Feature": [], "BugFix": [], "Enhancement": [], "Docs": [], "Other": []}

        commits = state["commits"]
        for i in range(0, len(commits), batch_size):
            batch = commits[i:i + batch_size]
            commits_text = "\n".join(batch)
            messages = prompt.format_messages(commits=commits_text)

            response = call_with_retry(llm, messages)

            try:
                json_str = extract_json_from_text(response.content)
                classified = json.loads(json_str)
                print(f"🔎 Batch {i//batch_size + 1} result:", json.dumps(classified, indent=2))

                # Merge batch results into global classification
                for k in all_classified.keys():
                    all_classified[k].extend(classified.get(k, []))

            except json.JSONDecodeError:
                print("❌ Failed to parse classification JSON. Output:\n", response.content)
                all_classified["Other"].extend(batch)

        return {"classified_commits": all_classified, "commits": commits}
    return classify


def call_with_retry(llm, messages, max_retries=20):
    for attempt in range(max_retries):
        try:
            return llm.invoke(messages)
        except RateLimitError as e:
            wait = None
            if hasattr(e, "message") and isinstance(e.message, str):
                match = re.search(r"(\d+)\s*seconds?", e.message)
                if match:
                    wait = int(match.group(1))

            # Fallback: exponential backoff
            if wait is None:
                wait = (2 ** attempt) + random.random()

            print(f"Rate limit hit. Waiting {wait:.2f}s before retry...")
            time.sleep(wait)
    raise RuntimeError("Max retries exceeded")


def make_summarize_node(llm, prompt, batch_size: int = 50):
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

            merged_summary = []
            for i in range(0, len(commits), batch_size):
                batch = commits[i:i + batch_size]
                messages = prompt.format_messages(commits="\n".join(batch), category=category)
                response = call_with_retry(llm, messages)
                merged_summary.append(response.content.strip())

            header = category_titles.get(category, category)
            section = f"### {header}\n\n" + "\n".join(merged_summary)
            output_sections.append(section)

        return {"release_notes": "\n\n".join(output_sections)}

    return summarize


def process_release_notes(commits: List[str], style_text: Optional[str] = None) -> str:
    backend = os.getenv("LLM_BACKEND", "azure").lower()

    if backend == "azure":
        deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT", "test")
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "https://aiopsvteam.openai.azure.com/")
        openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
        azure_auth = os.getenv("AZURE_AUTH", "aad").lower()

        if azure_auth == "key":
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError("AZURE_OPENAI_API_KEY must be set for Azure API key authentication.")
            llm = AzureChatOpenAI(
                model=deployment_name,
                azure_endpoint=azure_endpoint,
                api_version=openai_api_version,
                api_key=api_key,
            )
        else:
            # Default to Azure AD authentication
            token_provider = get_bearer_token_provider(
                DefaultAzureCredential(),
                "https://cognitiveservices.azure.com/.default"
            )
            llm = AzureChatOpenAI(
                model=deployment_name,
                azure_endpoint=azure_endpoint,
                api_version=openai_api_version,
                azure_ad_token_provider=token_provider,
            )
    elif backend == "openai":
        from langchain_openai import ChatOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set for OpenAI backend.")
        llm = ChatOpenAI(api_key=api_key)
    else:
        raise NotImplementedError(f"LLM backend '{backend}' is not supported yet.")

    classification_prompt = get_classification_prompt()
    summary_prompt = get_summary_prompt(style_sample=style_text)

    workflow = StateGraph(ReleaseNotesState)

    batch_size = 100
    classification_node = make_classification_node(llm, classification_prompt, batch_size)
    summarize_node = make_summarize_node(llm, summary_prompt, batch_size)

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
