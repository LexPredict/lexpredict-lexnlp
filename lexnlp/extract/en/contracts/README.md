# Contract Classification

*Date (ISO 8601): 2022-04-19*

---

## `Is-Contract?` Classifier

### Usage

Download the default Scikit-Learn pipeline:

```python
from lexnlp.ml.catalog.download import download_github_release
download_github_release('pipeline/is-contract/<version>')
```

Instantiate the classifier:

```python

from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorIsContract
probability_predictor_is_contract: ProbabilityPredictorIsContract = ProbabilityPredictorIsContract()
```

Use the `ProbabilityPredictorIsContract`

```python
probability_predictor_is_contract.is_contract(
    text='...',
    min_probability=0.5,
    return_probability=True,
)
```

### Training

Training processes can be found under `notebooks/classification/contracts/`

---

## Contract Type Classifier

*Not yet implemented*

