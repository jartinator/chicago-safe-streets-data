import config


def test_councilmatic_url_is_unhashed_base():
    # Must be the un-hashed base so the nightly content-hash change can't break us.
    assert config.COUNCILMATIC_DATASETTE_URL == "https://puddle.datamade.us/chicago_council"
