import shutil
from noteworthy.notes_generator import generate_release_notes
import pytest

@pytest.fixture(scope="module")
def cleanup_repo():
    # Setup: nothing
    yield
    # Teardown: remove cloned repo folder after tests
    shutil.rmtree("repo", ignore_errors=True)

def test_generate_release_notes(cleanup_repo):
    print("Test")
    repo_url = "https://github.com/microsoft/azure-linux-image-tools"
    notes = generate_release_notes(
        repo_url=repo_url,
        shoutout=True,
        highlight_section=False,
        output_format="markdown",
        exclude_patterns=["chore:", "docs:"]
    )
    assert notes is not None
