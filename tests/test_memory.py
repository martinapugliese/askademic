import pytest
from pydantic_ai.messages import ModelResponse, TextPart

from askademic.memory import Memory


@pytest.fixture
def memory():
    """Fixture to create a Memory instance."""
    return Memory(max_request_tokens=200)


@pytest.fixture
def mock_messages():
    """Fixture to create mock messages."""
    return [ModelResponse(parts=[TextPart("mock message")])]


def test_memory_initialization(memory):
    """Test that the memory initializes correctly."""
    assert memory._max_request_tokens == 200
    assert len(memory) == 0
    assert memory.get_messages() == []
    assert memory.get_total_tokens() == 0


def test_add_message(memory, mock_messages):
    """Test that a message can be added to the memory."""
    memory.add_message(100, mock_messages)
    assert len(memory) == 1
    assert memory.get_messages() == mock_messages
    assert memory.get_total_tokens() == 100


def test_add_multiple_messages(memory, mock_messages):
    """Test that the memory can add multiple messages."""
    memory.add_message(100, mock_messages)
    memory.add_message(200, mock_messages)
    assert len(memory) == 2
    assert memory.get_messages() == mock_messages * 2
    assert memory.get_total_tokens() == 200


def test_prune_history(memory, mock_messages):
    """Test that the memory prunes messages correctly."""
    memory.add_message(100, mock_messages)
    memory.add_message(200, mock_messages)
    memory.add_message(300, mock_messages)
    memory._prune_history()
    assert len(memory) == 2
    assert memory.get_total_tokens() == 200
    assert memory.get_messages() == mock_messages * 2


def test_clear_history(memory):
    """Test that the memory clears history correctly."""
    memory.add_message(100, mock_messages)
    memory.clear_history()
    assert len(memory) == 0
    assert memory.get_messages() == []
    assert memory.get_total_tokens() == 0
