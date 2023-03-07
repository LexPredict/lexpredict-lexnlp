__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs
from lexnlp.extract.en.contracts.contract_type_detector import ContractTypeDetector


def non_test_contract_type():
    model_folder = ''
    d2v_path = f'{model_folder}/d2v_size100_window10.json'
    rf_path = f'{model_folder}/rf_size100_window10_depth64'
    d = ContractTypeDetector(rf_path, d2v_path)

    with codecs.open(
            '/home/andrey/Downloads/src_files/text/src_txt_files/1274055_2010-03-23_4.txt',
            'r', encoding='utf-8') as fr:
        doc_text = fr.read()
    v = d.detect_contract_type_vector(doc_text)
    print(d.detect_contract_type(v, 0.15, 99, '?'))
    print(d.detect_contract_type(v, 0.15, 75, '?'))
    print(d.detect_contract_type(v, 0.19, 99, '?'))
