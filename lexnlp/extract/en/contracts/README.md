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

### Usage

Instantiate the classifier:

```python
from lexnlp.extract.en.contracts.predictors import ProbabilityPredictorContractType

predictor = ProbabilityPredictorContractType()
predictions = predictor.make_predictions("This Employment Agreement is entered into ...", top_n=3)
print(predictions)
```

Or infer a single label with thresholding:

```python
classification = predictor.detect_contract_type(
    "This Employment Agreement is entered into ...",
    min_probability=0.15,
    max_closest_probability=0.75,
    unknown_classification="",
)
print(classification)
```

### Runtime model tags

The default catalog tag for this predictor is `pipeline/contract-type/0.1`.
On modern Python runtimes, this legacy artifact may fail to unpickle.

When legacy loading fails and no explicit override is configured, the predictor
auto-falls back to a runtime-compatible tag: `pipeline/contract-type/0.2-runtime`.

You can explicitly select a tag at runtime:

```bash
export LEXNLP_CONTRACT_TYPE_MODEL_TAG="pipeline/contract-type/0.2-runtime"
```

### Bootstrap / Training

Build (or reuse) the runtime-compatible contract-type model from the released
corpus tag `corpus/contract-types/0.1`:

```bash
python scripts/bootstrap_assets.py --contract-type-model
```

Train explicitly and write a training summary report:

```bash
python scripts/train_contract_type_model.py \
  --target-tag pipeline/contract-type/0.2-runtime \
  --output-json artifacts/model_training/contract_type_model_training_report.json
```
