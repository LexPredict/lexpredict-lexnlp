import importlib
from pathlib import Path


def test_catalog_path_resolves_on_fresh_environment(tmp_path):
    import nltk.data
    import lexnlp.ml.catalog as catalog

    original_paths = list(nltk.data.path)
    try:
        candidate_root = tmp_path / "nltk_data"
        nltk.data.path = [str(candidate_root)]
        importlib.reload(catalog)

        assert catalog.CATALOG == candidate_root / "lexpredict-lexnlp"
        assert not catalog.CATALOG.exists()
    finally:
        nltk.data.path = original_paths
        importlib.reload(catalog)


def test_catalog_path_falls_back_to_home_when_nltk_path_empty(tmp_path, monkeypatch):
    import nltk.data
    import lexnlp.ml.catalog as catalog

    original_paths = list(nltk.data.path)
    original_home = Path.home()
    try:
        fake_home = tmp_path / "home"
        monkeypatch.setenv("HOME", str(fake_home))
        nltk.data.path = []
        importlib.reload(catalog)

        assert str(catalog.CATALOG).startswith(str(fake_home))
        assert catalog.CATALOG.name == "lexpredict-lexnlp"
        assert not catalog.CATALOG.exists()
    finally:
        nltk.data.path = original_paths
        monkeypatch.setenv("HOME", str(original_home))
        importlib.reload(catalog)
