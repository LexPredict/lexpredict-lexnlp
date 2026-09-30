"""Local Stanford adapters for NLTK's bytes-to-text Java output transition.

NLTK 3.10 returns text from ``internals.java`` while its deprecated Stanford
wrappers still unconditionally decode bytes. These subclasses retain NLTK's
command builders, output parsers, and verified Java invocation, adapting only
the temporary input and output handling.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
import os
from subprocess import PIPE
import tempfile

from nltk.internals import java
from nltk.tag import StanfordNERTagger as _StanfordNERTagger
from nltk.tag import StanfordPOSTagger as _StanfordPOSTagger
from nltk.tokenize.stanford import StanfordTokenizer as _StanfordTokenizer


def _java_text(output: str | bytes, encoding: str) -> str:
    if isinstance(output, str):
        return output
    if isinstance(output, bytes):
        return output.decode(encoding)
    raise TypeError("Stanford Java output must be text or bytes")


@contextmanager
def _temporary_input(data: bytes) -> Iterator[str]:
    path: str | None = None
    succeeded = False
    try:
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as stream:
            path = stream.name
            stream.write(data)
        # Close before Java reads the file, including on Windows.
        yield path
        succeeded = True
    finally:
        if path is not None:
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
            except OSError:
                if succeeded:
                    raise


class StanfordTokenizer(_StanfordTokenizer):
    """NLTK-compatible tokenizer accepting bytes or text from Java."""

    def _execute(self, cmd, input_, verbose=False):
        encoding = self._encoding
        command = list(cmd)
        command.extend(["-charset", encoding])
        if self._options_cmd:
            command.extend(["-options", self._options_cmd])
        data = input_.encode(encoding) if isinstance(input_, str) else input_
        with _temporary_input(data) as path:
            command.append(path)
            stdout, _stderr = java(
                command, classpath=self._stanford_jar, stdout=PIPE,
                stderr=PIPE, options=self.java_options,
            )
            return _java_text(stdout, encoding)


class _TextOutputTagger:
    def tag_sents(self, sentences):
        # The NER output parser needs the original sentence lengths after the
        # input has been serialized; materialize generators once for both uses.
        sentences = [list(sentence) for sentence in sentences]
        encoding = self._encoding
        data = "\n".join(" ".join(sentence) for sentence in sentences).encode(encoding)
        with _temporary_input(data) as path:
            self._input_file_path = path
            command = list(self._cmd)
            command.extend(["-encoding", encoding])
            stdout, _stderr = java(
                command, classpath=self._stanford_jar, stdout=PIPE,
                stderr=PIPE, options=self.java_options,
            )
            output = _java_text(stdout, encoding)
        return self.parse_output(output, sentences)


class StanfordPOSTagger(_TextOutputTagger, _StanfordPOSTagger):
    """NLTK-compatible POS tagger accepting bytes or text from Java."""


class StanfordNERTagger(_TextOutputTagger, _StanfordNERTagger):
    """NLTK-compatible NER tagger accepting bytes or text from Java."""
