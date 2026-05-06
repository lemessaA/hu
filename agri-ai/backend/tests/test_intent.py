"""Intent routing rules."""
from app.agent.nodes.intent import intent_node


def test_intent_weather_from_location():
    out = intent_node(
        {
            "user_input": "hello",
            "location": "Jimma",
        }
    )
    assert out["needs_weather"] is True
    assert out["intent"] in ("weather", "mixed")


def test_intent_weather_from_keyword():
    out = intent_node({"user_input": "Will it rain tomorrow?"})
    assert out["needs_weather"] is True
    assert out["intent"] == "weather"


def test_intent_crop_from_keyword():
    out = intent_node({"user_input": "My teff has leaf blight"})
    assert out["needs_crop"] is True
    assert out["intent"] == "crop"


def test_intent_mixed():
    out = intent_node(
        {"user_input": "Rain and disease on maize", "location": "Hawassa"}
    )
    assert out["needs_weather"] and out["needs_crop"]
    assert out["intent"] == "mixed"


def test_intent_general():
    out = intent_node({"user_input": "What is conservation agriculture?"})
    assert out["intent"] == "general"
    assert out["needs_knowledge"] is True
