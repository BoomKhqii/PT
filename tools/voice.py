

def set_voice_output(enabled: bool) -> dict:
    """Request that the orb enable or disable spoken replies."""
    if not isinstance(enabled, bool):
        raise ValueError("enabled must be True or False")

    return {
        "action": "set_voice_output",
        "enabled": enabled,
    }