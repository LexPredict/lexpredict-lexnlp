# `lexnlp.ml`

---

### `lexnlp.ml.catalog.CATALOG`

LexNLP stores downloaded data (Scikit-Learn pipelines, training corpora, etc.) in the `CATALOG` directory.
By default, `CATALOG` refers to the subdirectory `lexpredict-lexnlp` within NLTK's data directory (`nltk_data`).


### `lexnlp.ml.catalog.download`

Public functions:

`download_github_release(tag: str, prompt_user: bool = True) -> None`

    Downloads a GitHub release from the release repository, optionally confirming
    download behavior with a human user. This legacy API always returns `None`.

    If `prompt_user == True`:
        Prompt once with the manifest-pinned file size before downloading.

    Args:
        tag (str):
            The GitHub release tag to download.
        prompt_user (bool=True):
            Whether to prompt the user before downloading.

`download_github_release_to_path(tag: str, *, manifest_path=None, force=False) -> Path`

    Downloads and verifies a release without prompting, returning its installed
    path. Set `force=True` when the remote bytes must be fetched and checked even
    if a verified local copy already exists.

Downloaded files are written to the `CATALOG` directory.
Configure the release repository with `LEXNLP_MODELS_REPO` or
`LEXNLP_MODELS_REPO_SLUG`. Assigning the legacy `lexnlp.MODELS_REPO` or
`lexnlp.ml.catalog.download.MODELS_REPO` variable remains supported when
neither environment override is set.

Runtime-generated model candidates are stored under the private
`_local-candidates/` catalog namespace. Catalog lookup can use such a candidate
when the corresponding reviewed release is unavailable, but local bytes never
occupy the manifest-pinned release directory.

---

### `lexnlp.ml.normalizers`



The `Normalizer` class searches for and replaces substrings in input text.

It is initialized with an iterable of tuples. Each tuple should contain a function which takes a string as input and yields a subclass of `lexnlp.extract.common.annotations.text_annotation.TextAnnotation`:

```python
Callable[[str], Generator[TextAnnotation, None, None]]
```
The second element of each tuple should be a replacement string.

Usage:

```python
>>> from lexnlp.ml.normalizers import Normalizer

>>> normalizer: Normalizer = Normalizer(
...     normalizations=(
...         (get_ratio_annotations, '__RATIO__'),
...         (get_date_annotations, '__DATE__'),
...         (get_percent_annotations, '__PERCENT__'),
...         (get_amount_annotations, '__AMOUNT__'),
...     ),
... )

>>> normalizer(text='7% is due on 2022-01-01')
'__PERCENT__ is due on __DATE__'

```

---

### `lexnlp.ml.gensim_utils`

`lexnlp.ml.gensim_utils.TrainingCallback` is used for printing Gensim training information. Read more here: https://radimrehurek.com/gensim/models/callbacks.html
        

```python
doc2vec_model: Doc2Vec = Doc2Vec(
    ...,
    callbacks=(TrainingCallback(),)
)
```

`lexnlp.ml.gensim_utils.DummyGensimKeyedVectors` is a drop-in replacement for Gensim's `KeyedVectors` and is useful for reducing file size.

Note: models must be saved with `cloudpickle`, or DummyGensimKeyedVectors must be imported before a model loaded from disk. 

```python
doc2vec_model.dv = DummyGensimKeyedVectors(doc2vec_model.dv.vector_size)
```

---

### `lexnlp.ml.predictor`

Subclasses of `lexnlp.ml.predictor.ProbabilityPredictor` should use a Scikit-Learn Pipeline to transform input and make classification predictions.

---

### `lexnlp.ml.sklearn_transformers`

Scikit-Learn transformers for usage in Scikit-Learn Pipelines. Read more here: https://scikit-learn.org/stable/data_transforms.html


### `lexnlp.ml.vectorizers`

Classes in this module form vector representations of strings.
