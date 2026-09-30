"""Scoped loaders for historical LexNLP model artifacts.

Pickle and Joblib files can execute arbitrary code.  These helpers are only
for trusted LexNLP model artifacts; they do not make unpickling safe.
"""

from __future__ import annotations

import copy
import inspect
import os
import pickle
import re
import warnings
from contextvars import ContextVar
from dataclasses import dataclass

import numpy as np
import sklearn
from joblib import numpy_pickle
from sklearn.base import BaseEstimator
from sklearn.ensemble._base import BaseEnsemble
from sklearn.tree import DecisionTreeClassifier, _tree


@dataclass
class CompatibilityReport:
    """Counts of compatibility repairs applied during one scoped load."""

    legacy_tree_upgrades: int = 0
    estimator_attribute_upgrades: int = 0
    classifier_value_normalizations: int = 0


_ACTIVE_REPORT: ContextVar[CompatibilityReport | None] = ContextVar(
    "lexnlp_sklearn_compatibility_report",
    default=None,
)


def _coerce_legacy_tree_nodes(nodes: np.ndarray) -> np.ndarray:
    """Adapt the one known pre-1.3 sklearn tree-node dtype migration."""

    expected_dtype = getattr(_tree, "NODE_DTYPE", None)
    expected_names = getattr(expected_dtype, "names", None)
    actual_names = getattr(getattr(nodes, "dtype", None), "names", None)
    if expected_names is None or actual_names is None or nodes.dtype == expected_dtype:
        return nodes

    expected_set = set(expected_names)
    actual_set = set(actual_names)
    if expected_set - actual_set != {"missing_go_to_left"} or actual_set - expected_set:
        return nodes
    if any(nodes.dtype[name] != expected_dtype[name] for name in actual_names):
        return nodes

    converted = np.zeros(nodes.shape, dtype=expected_dtype)
    for name in actual_names:
        converted[name] = nodes[name]
    report = _ACTIVE_REPORT.get()
    if report is not None:
        report.legacy_tree_upgrades += 1
    return converted


PATCHED_TREE_CLASS = None
if "missing_go_to_left" in (getattr(_tree.NODE_DTYPE, "names", None) or ()):

    class PatchedTree(_tree.Tree):
        """Tree subclass used only while a LexNLP artifact is unpickled."""

        def __setstate__(self, state):  # type: ignore[override]
            if isinstance(state, dict) and "nodes" in state:
                nodes = _coerce_legacy_tree_nodes(state["nodes"])
                if nodes is not state["nodes"]:
                    state = dict(state)
                    state["nodes"] = nodes
            elif isinstance(state, tuple) and state:
                nodes = _coerce_legacy_tree_nodes(state[0])
                if nodes is not state[0]:
                    state = (nodes,) + tuple(state[1:])
            return _tree.Tree.__setstate__(self, state)

    PatchedTree.__name__ = "Tree"
    PatchedTree.__qualname__ = "Tree"
    PatchedTree.__module__ = "sklearn.tree._tree"
    PATCHED_TREE_CLASS = PatchedTree


class _SklearnCompatibilityMixin:
    def find_class(self, module, name):
        if module == "sklearn.tree.tree":
            module = "sklearn.tree"
        elif module == "sklearn.ensemble.forest":
            module = "sklearn.ensemble._forest"
        elif module == "sklearn.tree._tree" and name == "Tree" and PATCHED_TREE_CLASS is not None:
            return PATCHED_TREE_CLASS
        return super().find_class(module, name)


class RenameUnpickler(_SklearnCompatibilityMixin, pickle.Unpickler):
    """Unpickler with LexNLP's historical sklearn class-name mappings."""


class _LexNLPNumpyUnpickler(
    _SklearnCompatibilityMixin,
    numpy_pickle.NumpyUnpickler,
):
    """Joblib unpickler whose compatibility rules are local to one load."""


def _sklearn_uses_proportional_tree_values() -> bool:
    version_match = re.match(r"^(\d+)\.(\d+)", sklearn.__version__)
    if version_match is None:
        return False
    major_minor = tuple(int(part) for part in version_match.groups())
    return major_minor >= (1, 4)


_SKLEARN_USES_PROPORTIONAL_TREE_VALUES = _sklearn_uses_proportional_tree_values()
_JOBLIB_SUPPORTS_NATIVE_BYTE_ORDER = (
    "ensure_native_byte_order" in inspect.signature(numpy_pickle.NumpyUnpickler).parameters
)


def _iter_model_children(model):
    if isinstance(model, type):
        return
    if isinstance(model, dict):
        yield from model.values()
    elif isinstance(model, np.ndarray) and model.dtype.hasobject:
        yield from model.flat
    elif isinstance(model, (list, tuple, set)):
        yield from model

    if hasattr(model, "__dict__"):
        yield from vars(model).values()


def _new_estimator_with_current_defaults(model):
    kwargs = {}
    try:
        signature = inspect.signature(type(model))
    except (TypeError, ValueError):
        return None

    for parameter in signature.parameters.values():
        if parameter.kind in (
            inspect.Parameter.VAR_POSITIONAL,
            inspect.Parameter.VAR_KEYWORD,
        ):
            continue
        if parameter.default is inspect.Parameter.empty:
            if not hasattr(model, parameter.name):
                return None
            kwargs[parameter.name] = getattr(model, parameter.name)
    try:
        return type(model)(**kwargs)
    except (TypeError, ValueError):
        return None


def _modernize_patched_trees(value, memo=None):
    """Replace migration-only Tree instances before returning to callers."""
    if memo is None:
        memo = {}

    value_id = id(value)
    if value_id in memo:
        return memo[value_id]

    if PATCHED_TREE_CLASS is not None and isinstance(value, PATCHED_TREE_CLASS):
        native_tree = _tree.Tree(
            value.n_features,
            value.n_classes,
            value.n_outputs,
        )
        native_tree.__setstate__(value.__getstate__())
        memo[value_id] = native_tree
        return native_tree

    memo[value_id] = value
    if isinstance(value, type):
        return value
    if isinstance(value, list):
        for index, item in enumerate(value):
            value[index] = _modernize_patched_trees(item, memo)
    elif isinstance(value, tuple):
        converted = tuple(_modernize_patched_trees(item, memo) for item in value)
        memo[value_id] = converted
        return converted
    elif isinstance(value, dict):
        for key, item in list(value.items()):
            value[key] = _modernize_patched_trees(item, memo)
    elif isinstance(value, np.ndarray) and value.dtype.hasobject:
        for index, item in enumerate(value.flat):
            value.flat[index] = _modernize_patched_trees(item, memo)
    elif hasattr(value, "__dict__"):
        for name, item in list(vars(value).items()):
            setattr(value, name, _modernize_patched_trees(item, memo))
    return value


def restore_legacy_model_state(model, report=None):
    """Restore known sklearn state migrations after a scoped model load."""

    report = report or CompatibilityReport()
    seen = set()
    pending = [model]
    while pending:
        current = pending.pop()
        current_id = id(current)
        if current_id in seen:
            continue
        seen.add(current_id)

        if isinstance(current, BaseEnsemble):
            state = getattr(current, "__dict__", {})
            if "estimator" not in state and "base_estimator" in state:
                current.estimator = state["base_estimator"]
                report.estimator_attribute_upgrades += 1
            if "estimator_" not in state and "base_estimator" in state:
                current.estimator_ = state["base_estimator"]
                report.estimator_attribute_upgrades += 1

        if isinstance(current, BaseEstimator):
            fresh = _new_estimator_with_current_defaults(current)
            if fresh is not None:
                for name, default in vars(fresh).items():
                    if not hasattr(current, name):
                        setattr(current, name, copy.deepcopy(default))
                        report.estimator_attribute_upgrades += 1

            if hasattr(current, "sigma_") and not hasattr(current, "var_"):
                current.var_ = current.sigma_
                report.estimator_attribute_upgrades += 1
            if hasattr(current, "var_") and not hasattr(current, "variance_"):
                current.variance_ = current.var_
                report.estimator_attribute_upgrades += 1

        if (
            _SKLEARN_USES_PROPORTIONAL_TREE_VALUES
            and isinstance(current, DecisionTreeClassifier)
            and hasattr(current, "tree_")
        ):
            values = current.tree_.value
            normalizers = values.sum(axis=2, keepdims=True)
            populated = normalizers != 0
            if np.any(populated & ~np.isclose(normalizers, 1.0)):
                np.divide(
                    values,
                    normalizers,
                    out=values,
                    where=populated,
                )
                report.classifier_value_normalizations += 1

        pending.extend(_iter_model_children(current))
    return model


def renamed_load(file_obj, *, report=None):
    """Load a trusted plain-pickle LexNLP model with local compatibility."""

    report = report or CompatibilityReport()
    token = _ACTIVE_REPORT.set(report)
    try:
        value = RenameUnpickler(file_obj).load()
    finally:
        _ACTIVE_REPORT.reset(token)
    value = _modernize_patched_trees(value)
    return restore_legacy_model_state(value, report)


def load_sklearn_model(file_obj, *, report=None):
    """Load one trusted pickle/cloudpickle sklearn artifact compatibly."""

    return renamed_load(file_obj, report=report)


def _new_joblib_unpickler(filename, file_handle, mmap_mode):
    if _JOBLIB_SUPPORTS_NATIVE_BYTE_ORDER:
        return _LexNLPNumpyUnpickler(
            filename,
            file_handle,
            ensure_native_byte_order=mmap_mode is None,
            mmap_mode=mmap_mode,
        )
    return _LexNLPNumpyUnpickler(
        filename,
        file_handle,
        mmap_mode=mmap_mode,
    )


def _unpickle_joblib(file_handle, filename, mmap_mode, report):
    unpickler = _new_joblib_unpickler(filename, file_handle, mmap_mode)
    try:
        token = _ACTIVE_REPORT.set(report)
        try:
            loaded = unpickler.load()
        finally:
            _ACTIVE_REPORT.reset(token)
        loaded = _modernize_patched_trees(loaded)
        value = restore_legacy_model_state(loaded, report)
        if unpickler.compat_mode:
            warnings.warn(
                "The file was generated by Joblib before 0.10; regenerate this LexNLP model artifact.",
                DeprecationWarning,
                stacklevel=3,
            )
        return value
    except UnicodeDecodeError as exc:
        error = ValueError("Python 2 Joblib pickles are not supported; regenerate this LexNLP model artifact.")
        error.__cause__ = exc
        raise error


def load_joblib_model(file_obj, mmap_mode=None, *, report=None):
    """Load one trusted LexNLP Joblib artifact without mutating Joblib globals."""

    report = report or CompatibilityReport()
    if hasattr(file_obj, "read"):
        filename = getattr(file_obj, "name", "")
        with numpy_pickle._validate_fileobject_and_memmap(
            file_obj,
            filename,
            mmap_mode,
        ) as (validated_file, validated_mmap_mode):
            return _unpickle_joblib(
                validated_file,
                filename,
                validated_mmap_mode,
                report,
            )

    filename = os.fspath(file_obj)
    with (
        open(filename, "rb") as raw_file,
        numpy_pickle._validate_fileobject_and_memmap(
            raw_file,
            filename,
            mmap_mode,
        ) as (validated_file, validated_mmap_mode),
    ):
        if isinstance(validated_file, str):
            # Joblib <=0.9 used a separate persistence format.  None of the
            # supported LexNLP artifacts use it, but retain Joblib's
            # compatibility behaviour for callers of this legacy API.
            return restore_legacy_model_state(
                numpy_pickle.load_compatibility(validated_file),
                report,
            )
        return _unpickle_joblib(
            validated_file,
            filename,
            validated_mmap_mode,
            report,
        )
