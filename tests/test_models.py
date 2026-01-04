"""
Tests pour les modèles d'IA
"""
import pytest
from auto_antigravity.models.factory import ModelFactory


def test_create_gemini_model():
    """Test la création d'un modèle Gemini"""
    model = ModelFactory.create_model(
        "gemini",
        api_key="test_key"
    )
    
    assert model.model_name == "gemini-3-pro"
    assert model.api_key == "test_key"


def test_create_claude_model():
    """Test la création d'un modèle Claude"""
    model = ModelFactory.create_model(
        "claude",
        api_key="test_key"
    )
    
    assert model.model_name == "claude-sonnet-4.5"
    assert model.api_key == "test_key"


def test_create_openai_model():
    """Test la création d'un modèle OpenAI"""
    model = ModelFactory.create_model(
        "openai",
        api_key="test_key"
    )
    
    assert model.model_name == "gpt-4"
    assert model.api_key == "test_key"


def test_invalid_model_type():
    """Test la création d'un modèle avec un type invalide"""
    with pytest.raises(ValueError, match="Type de modèle non supporté"):
        ModelFactory.create_model(
            "invalid_type",
            api_key="test_key"
        )


def test_custom_model_name():
    """Test la création d'un modèle avec un nom personnalisé"""
    model = ModelFactory.create_model(
        "openai",
        api_key="test_key",
        model_name="gpt-3.5-turbo"
    )
    
    assert model.model_name == "gpt-3.5-turbo"


def test_available_models():
    """Test la récupération des modèles disponibles"""
    models = ModelFactory.available_models()
    
    assert "gemini" in models
    assert "claude" in models
    assert "openai" in models
