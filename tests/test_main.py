import pytest

from askademic.constants import CLAUDE_HAIKU_3_5_MODEL_ID, GEMINI_2_FLASH_MODEL_ID
from askademic.utils import choose_model


def test_choose_model():
    assert choose_model("gemini") == GEMINI_2_FLASH_MODEL_ID
    assert choose_model("claude") == CLAUDE_HAIKU_3_5_MODEL_ID


def test_choose_model_invalid():
    with pytest.raises(ValueError) as excinfo:
        choose_model("invalid")
    assert "Invalid model family" in str(excinfo.value)
