from __future__ import annotations


from lexnlp import DEFAULT_MODELS_REPO, get_models_repo


def test_get_models_repo_default(monkeypatch) -> None:
    monkeypatch.delenv("LEXNLP_MODELS_REPO", raising=False)
    monkeypatch.delenv("LEXNLP_MODELS_REPO_SLUG", raising=False)

    assert get_models_repo() == DEFAULT_MODELS_REPO


def test_get_models_repo_explicit_url_adds_trailing_slash(monkeypatch) -> None:
    monkeypatch.setenv(
        "LEXNLP_MODELS_REPO",
        "https://api.github.com/repos/foo/bar/releases/tags",
    )
    monkeypatch.delenv("LEXNLP_MODELS_REPO_SLUG", raising=False)

    assert get_models_repo() == "https://api.github.com/repos/foo/bar/releases/tags/"


def test_get_models_repo_slug(monkeypatch) -> None:
    monkeypatch.delenv("LEXNLP_MODELS_REPO", raising=False)
    monkeypatch.setenv("LEXNLP_MODELS_REPO_SLUG", "foo/bar")

    assert get_models_repo() == "https://api.github.com/repos/foo/bar/releases/tags/"


def test_get_models_repo_url_precedence_over_slug(monkeypatch) -> None:
    monkeypatch.setenv(
        "LEXNLP_MODELS_REPO",
        "https://api.github.com/repos/a/b/releases/tags/",
    )
    monkeypatch.setenv("LEXNLP_MODELS_REPO_SLUG", "foo/bar")

    assert get_models_repo() == "https://api.github.com/repos/a/b/releases/tags/"

