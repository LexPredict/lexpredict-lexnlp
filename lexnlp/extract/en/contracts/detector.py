"""
Detect whether document is a contract.
"""

import os
import pickle

# Third-party imports
import gensim.models.doc2vec
from sklearn.externals import joblib

# LexNLP
from lexnlp.nlp.en.segments.sentences import get_sentence_list
from lexnlp.nlp.en.tokens import get_stem_list


__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2019, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/master/LICENSE"
__version__ = "0.2.5"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')

# Load doc2vec model
d2v_model_filename = "d2v_all_size100_window10.model"
d2v_model_path = os.path.join(data_dir, d2v_model_filename)

# Load doc2vec model from part files like d2v_all_size100_window10.model.part.aa
if os.path.exists(d2v_model_path):
    d2v_model = gensim.models.doc2vec.Doc2Vec.load(d2v_model_path)
else:
    d2v_model_filenames = sorted([i for i in os.listdir(data_dir)
                                  if i.startswith('{}.part.'.format(d2v_model_filename))])
    if not d2v_model_filenames:
        raise RuntimeError('Doc2Vec model file "{}" not found'.format(d2v_model_filename))
    d2v_model_pickled = b''
    for filename in d2v_model_filenames:
        d2v_model_pickled += open(os.path.join(data_dir, filename), 'rb').read()
    d2v_model = pickle.loads(d2v_model_pickled)


# Load classifier model
rf_model = joblib.load(
    os.path.join(data_dir, "is_contract_classifier.pickle"))


# Utility methods
def process_sentence(sentence):
    return [s for s in get_stem_list(sentence, stopword=True, lowercase=True) if s.isalpha()]


def process_document(document):
    doc_words = []
    for sentence in get_sentence_list(document):
        doc_words.extend(process_sentence(sentence))
    return doc_words


def is_contract(text, min_probability=0.5, return_probability=False):
    # Create the vector representation from doc2vec model
    text_vector = d2v_model.infer_vector(process_document(text))

    # Pass vector into classifier
    try:
        classifier_score = rf_model.predict_proba([text_vector])[0, 1]
    except IndexError:
        return None

    ret = bool(classifier_score >= min_probability)

    if return_probability:
        ret = (ret, classifier_score)

    return ret
