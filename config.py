"""Configuration and environment loading."""

from dataclasses import dataclass

from dotenv import load_dotenv


# 1) imports and setup
# 2) load environment variables
load_dotenv()


@dataclass
class ModelSettings:
    """Simple beginner-friendly model settings."""

    openai_model_name: str = "gpt-4o-mini"
    ollama_model_name: str = "mistral"

    # 4) model parameters (temperature strict vs creative)
    strict_temperature: float = 0.1
    creative_temperature: float = 0.8


SETTINGS = ModelSettings()


def get_temperature(creativity_mode: str) -> float:
    """Return temperature based on selected mode."""
    if creativity_mode.lower() == "creative":
        return SETTINGS.creative_temperature
    return SETTINGS.strict_temperature
