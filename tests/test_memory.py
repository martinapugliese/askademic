from askademic.memory import Memory
import pytest
from unittest.mock import MagicMock, patch
from pydantic_ai.messages import ModelResponse, TextPart
 


@pytest.fixture
def memory():
    return Memory(max_request_tokens=200)

@pytest.fixture
def mock_messages():
    return [ModelResponse(parts=[TextPart("mock message")])]

def test_memory_initialization(memory):
    assert memory._max_request_tokens == 200
    assert len(memory) == 0
    assert memory.get_last_message() is None
    assert memory.get_last_message_tokens() == 0

def test_add_message(memory, mock_messages):
    memory.add_message(100, mock_messages)
    assert len(memory) == 1
    assert memory.get_last_message() == mock_messages
    assert memory.get_last_message_tokens() == 100

def test_add_multiple_messages(memory, mock_messages):
    memory.add_message(100, mock_messages) 
    memory.add_message(200, mock_messages)
    assert len(memory) == 2
    assert memory.get_last_message() == mock_messages
    assert memory.get_last_message_tokens() == 200


def test_prune_history(memory):
    memory.add_message(100, mock_messages)
    memory.add_message(200, mock_messages)
    memory.add_message(300, mock_messages)
    memory._prune_history()
    assert len(memory) == 2
    assert memory.get_last_message_tokens() == 200

    memory.add_message(400, mock_messages)
    memory._prune_history()
    assert len(memory) == 1
    assert memory.get_last_message_tokens() == 200


def test_clear_history(memory):
    memory.add_message(100, mock_messages)
    memory.clear_history()
    assert len(memory) == 0
    assert memory.get_last_message() is None
    assert memory.get_last_message_tokens() == 0




