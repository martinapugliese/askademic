import logging
from datetime import datetime
from typing import Dict, List

from pydantic_ai.messages import ModelMessage

today = datetime.now().strftime("%Y-%m-%d")

logging.basicConfig(level=logging.INFO, filename=f"{today}_logs.txt")
logger = logging.getLogger(__name__)


class Memory:
    def __init__(self, max_request_tokens=2e5):
        self._max_request_tokens = max_request_tokens
        self._message_history: List[Dict[str, int | ModelMessage]] = []

    def __len__(self):
        return len(self._message_history)

    def __iter__(self):
        return iter(self._message_history)

    def __getitem__(self, index):
        return self._message_history[index]

    def _prune_history(self):
        """Prune the message history to fit within the token limit."""
        total_tokens = self.get_total_tokens()
        while total_tokens > self._max_request_tokens:
            _ = self._message_history.pop(0)
            if len(self._message_history) == 0:
                break
            total_tokens = self.get_total_tokens()

        total_tokens = self.get_total_tokens()
        logger.info(
            f"{datetime.now()}: Pruned messages, current total tokens: {total_tokens}"
        )

    def add_message(self, message_tokens: int, message: ModelMessage):
        """Add a message to the memory."""
        total_tokens = self.get_total_tokens()
        message_tokens = message_tokens - total_tokens
        self._message_history.append(
            {"message_tokens": message_tokens, "message": message}
        )

        total_tokens = self.get_total_tokens()
        logger.info(
            f"{datetime.now()}: Adding messages, current total tokens: {total_tokens}"
        )

    def get_messages(self):
        """Get the message history."""
        messages = []
        for m in self._message_history:
            messages += m["message"]
        return messages

    def clear_history(self):
        """Clear the message history."""
        self._message_history = []

    def get_total_tokens(self):
        """Get the total number of tokens in the message history."""
        if len(self._message_history) == 0:
            return 0
        return sum([m["message_tokens"] for m in self._message_history])
