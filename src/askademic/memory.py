import logging
from typing import List, Dict
from pydantic_ai.messages import ModelMessage

logging.basicConfig(level=logging.INFO, filename="logs.txt")
logger = logging.getLogger(__name__)

class Memory:

    def __init__(self, max_request_tokens=5e5):
        self._max_request_tokens = max_request_tokens
        self._message_history: List[Dict[str, int | ModelMessage]] = []

    def __len__(self):  
        return len(self._message_history)
    
    def __iter__(self):
        return iter(self._message_history)
    
    def __getitem__(self, index):
        return self._message_history[index]
    
    def _prune_history(self):
        total_tokens = self._message_history[-1]["total_tokens"]
        while total_tokens > self._max_request_tokens:
            first_message_tokens = self._message_history.pop(0)["total_tokens"]
            if len(self._message_history) == 0:
                break
            for m in self._message_history:
                m["total_tokens"] -= first_message_tokens
            total_tokens = self._message_history[-1]["total_tokens"]

        logger.info(f"*** Pruned messages, current total tokens: {total_tokens}")

    def add_message(self, total_tokens: int, message: ModelMessage):

        if total_tokens > self.get_last_message_tokens():

            logger.info(f"*** Adding messages current total tokens: {total_tokens}")
            self._message_history.append({
                "total_tokens": total_tokens,
                "message": message
            })

    def get_messages(self):
        messages = []
        for m in self._message_history:
            messages+=m["message"]
        return messages 
    
    def clear_history(self):
        self._message_history = []

    def get_last_message(self): 
        return self._message_history[-1]["message"] if self._message_history else None
    
    def get_last_message_tokens(self):  
        return self._message_history[-1]["total_tokens"] if self._message_history else 0


