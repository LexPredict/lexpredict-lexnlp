__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2021, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-lexnlp/blob/2.3.0/LICENSE"
__version__ = "2.3.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


import codecs
import joblib
import os
import string
import unicodedata

from collections import OrderedDict

import pandas
import sklearn
import sklearn.linear_model
import sklearn.svm
import sklearn.ensemble

from lexnlp.nlp.train.train_data_manager import ensure_documents_in_folder


SECTION_BREAK_POSITIONS = {
    '/samples/agreements/construction/1002047_1999-08-31_CONSTRUCTION MANAGEMENT AGREEMENT.txt':
        [219, 443, 792, 829, 884, 1164, 1307, 1326, 1592, 1840, 1902, 2007, 2062, 2120],
    '/samples/agreements/construction/1011109_2000-08-14_CONSTRUCTION AGREEMENT (ADDISON).txt':
        [75, 97, 113, 140, 178, 231, 269, 286, 298, 315, 334, 419],  # the last section is 'Exhibit...'
    '/samples/agreements/construction/1011109_2000-08-14_CONSTRUCTION AGREEMENT (BALLANTYNE).txt':
        [78, 100, 116, 142, 180, 232, 271, 288, 300, 317, 335, 426],  # the last section is also 'Exhibit...'
    '/samples/agreements/employment/1046578_2006-08-08_EX-10.32(A) AMENDMENT TO EMPLOYMENT AGREEMENT.txt': [58, 77, 187],
    '/samples/agreements/employment/1025953_2005-02-11_EMPLOYMENT AGREEMENT BETWEEN NOVASTAR FINANCIAL, INC. AND GREGORY S. METZ.txt':
        [18, 50, 52, 58, 64, 72, 77, 82, 96, 104, 170, 204, 219, 247, 262, 300, 343, 368, 376, 406, 411, 416, 435,
         440, 446, 451, 456, 493, 499, 516],
    '/samples/agreements/employment/1001250_2013-02-27_AMENDMENT TO EMPLOYMENT AGREEMENT-CEDRIC PROUVE.txt':
        [77, 100, 118, 294, ],
    '/samples/agreements/employment/1016439_1998-05-15_STEPHEN A. CARNS EMPLOYMENT AGREEMENT.txt':
        [111, 113, 162, 174, 192, 197, 207, 314, 384, 433, 469, 507, 520, 530, 540, 542, 565, 589, 596, 606, 626],
    '/samples/agreements/employment/102379_2000-09-12_EMPLOYMENT AGREEMENT.txt':
        [15, 24, 26, 31, 39, 52, 70, 78, 83, 87, 98, 104, 114, 116, 125, 130, 132, 144, 174,
         192, 197, 199, 208, 221, 226, 230, 235, 243],
    '/samples/agreements/employment/18396_2005-09-12_EVP CFO EMPLOYMENT AGREEMENT.txt': [],
    '/samples/agreements/employment/17843_2007-07-11_EXHIBIT 99.2 EMPLOYMENT AGREEMENT.txt': [],
    '/samples/agreements/employment/1001916_2007-12-06_EMPLOYMENT AGREEMENT.txt':
        [21, 29, 32, 36, 39, 50, 52, 56, 59, 60, 74, 91, 92, 94],
    '/samples/agreements/employment/1013761_2000-08-04_EMPLOYMENT AGREEMENT.txt':
        [24, 28, 30, 37, 44, 46, 68, 77, 84, 88, 93, 98, 105, 109, 114, 119, 170, 199],
    '/samples/agreements/employment/1013796_2007-10-01_AMENDMENT TO A. SHUCKHART EMPLOYMENT AGREEMENT.txt':
        [69, 120, 192, ],
    '/samples/agreements/employment/1014507_2012-10-05_LETTER AMENDMENT TO AMENDED AND RESTATED EMPLOYMENT AGREEMENT.txt':
        [54, 59, 64],
    '/samples/agreements/employment/1017829_1999-11-15_EMPLOYMENT AGREEMENT - KELLEY WOOD.txt': [],
    '/samples/agreements/employment/1031296_2004-11-04_EX-10.41 EMPLOYMENT AGREEMENT.txt':
        [58, 65, 83, 143, 152, 198, 222, 250, 256, 259],
    '/samples/agreements/employment/1036044_2011-05-05_EXECUTIVE EMPLOYMENT AGREEMENT.txt':
        [21, 35, 40, 57, 59, 61, 64, 66, 70, 72, 75, 78, 108, 113, 135, 144, 155, 164, 181, 190, 197],
    '/samples/agreements/employment/1037114_1997-08-25_EMPLOYMENT AGREEMENT BETWEEN D. CRANTS, III.txt':
        [31, 41, 43, 52, 56, 91, 95, 97, 114, 132, 147, 151, 153, 158, 175, 180, 193, 200, 205, 209],
    '/samples/agreements/employment/1043186_2013-01-23_EMPLOYMENT AGREEMENT WITH ANDREW L. PUHALA.txt':
        [28, 33, 38, 43, 47, 54, 59, 63, 69, 76, 90, 95, 102, 107, 112, 117, 123],
    '/samples/agreements/employment/1060846_2002-08-14_EMPLOYMENT AGREEMENT - HARPER.txt':
        [36, 54, 63, 87, 95, 105, 116, 152, 193, 237, 244, 251, 255, 261, 269, 273, 276, 283],
    '/samples/agreements/employment/1081290_2003-08-14_EMPLOYMENT AGREEMENT BY AND BETWEEN REDBACK NETWORKS, INC..txt':
        [25, 30, 37, 43, ],
    '/samples/agreements/software_license/1100644_2016-11-21_SOFTWARE LICENSE AGREEMENT.txt':
        [21, 25, 29, 33, 37, 41, 45, 49, 67, 71, 75, 79, 83, 87, 91, 95, 99118, 122, 126, 130, 134,
         138, 142, 167, 171, 175, 179, 185, 207, 211, 215, 219, 228, 235, 266, 270, 274, 278, 282,
         304, 308, 312, 316, 359, 369, 389, 486, 512, 514, 518, 522, 528, 532, 550, 552, 556, 558,
         562, 568, 570, 574, 576, 580, 584, 588, 592, 611, 615, 617, 621, 625, 629],
    '/samples/agreements/software_license/1000297_1999-03-16_SOFTWARE LICENSE AGREEMENT.txt':
        [49, 67, 78, 103, 143, 155, 228, 283, 320, 327, 415, 458, 470, ],
    '/samples/agreements/software_license/1004232_1997-08-14_SOFTWARE LICENSE AGREEMENT DATED AS OF 5 13 97.txt':
        [25, 57, 68, 102, 129, 149, 179, 202, 226, 237, 292, 294, 299, 316, 332, 345, 387, 396, 405,
         407, 436, 440, 444, 451, 463, 470, 476],
    '/samples/agreements/software_license/1000495_2003-03-26_AMENDMENT TO OEM-IN SOFTWARE LICENSE AGREEMENT.txt':
        [59, 63, 80, 128, 145, 147, 150, 156, 183, 185, 191, 193, 205, 211, 232, 244, 253, 265,
         267, 372, 376, 383, 390, 393, 396, 399,
         401, 413, 488, 490, 506, 521, 574, 607, 623, 625, 639, 660, 677, 679, 749, 751, 769,
         780, 788, 824, 907, 911, 913, 926, 931, 944, 949],
    '/samples/agreements/software_license/1010026_1997-08-13_SOFTWARE LICENSE AND CO-MARKETING AGREEMENT.txt':
        [48, 85, 87, 97, 110, 131, 141, 160, 164, 197, 211, 215, 234, 251, 255, 259,
         259, 264, 301, 303, 346, 361, 368, 370, 409, 413, 434, 436, 446, 455, 457, 461, 476,
         484, 499, 507, 512, 522, 593],
    '/samples/agreements/software_license/906595_1998-08-19_SOFTWARE LICENSE AGREEMENT.txt':
        [58, 85, 100, 102, 108, 127, 132, 148, 160, 163, 179, 201, 228, 262, 270, 280, 300, 330,
         332, 348, 373, 427, 443, 462, 464, 474, 502, 512, 530, 540, 555, 560, 566, 612, 627, 633, 696,
         719, 738, 753, 795, 808, 844],
    '/samples/agreements/software_license/1582586_2015-08-31_SOFTWARE LICENSE AND ROYALTY AGREEMENT.txt':
        [20, 73, 125, 152, 198, 219, 263, 286, 357, 363, 378, 387, 395, 403, 412, 422, 430, 438,
         446, 453, 517, 597, 637]
}


class SectionSegmentizerTrainManager:
    def __init__(self):
        # Model parameters
        self.line_window_pre = 3
        self.line_window_post = 3

        # Setup feature and target data
        self.feature_data = []
        self.target_data = []
        self.feature_df = None

    def build_features(
            self,
            samples_repository_path: str,
            target_path: str):
        section_break_positions = ensure_documents_in_folder(
            SECTION_BREAK_POSITIONS,
            target_path,
            OrderedDict({'/samples/': samples_repository_path}))

        # Iterate through files and test
        for file_name in sorted(list(section_break_positions.keys())):
            # Read and get doc distribution
            with codecs.open(file_name, 'r', encoding='utf-8') as file_buffer:
                file_text = file_buffer.read()
                doc_distribution = self._build_document_distribution(file_text)

            # Split to lines and iterate
            file_lines = file_text.splitlines()
            for line_id in range(len(file_lines)):
                self.feature_data.append(
                    self._build_section_break_features(
                        file_lines,
                        line_id,
                        include_doc=doc_distribution))
                self.target_data.append(1 if line_id in section_break_positions[file_name] else 0)
                if self.target_data[-1] == 1:
                    # print((file_name, line_id, target_data[-1]))
                    # print(file_lines[line_id])
                    pass
                # Convert to DF
        self.feature_df = pandas.DataFrame(self.feature_data).fillna(-1)
        print(f'Feature df dimensions: {self.feature_df.shape}')

    def train_logistic_regression(self):
        # Build model
        model_log = sklearn.linear_model.LogisticRegression(penalty='l1', C=10.0, solver='lbfgs')
        model_log.fit(self.feature_df, self.target_data)

        # Assess model
        predicted_log = model_log.predict(self.feature_df)
        print(sklearn.metrics.classification_report(self.target_data, predicted_log))
        print(sklearn.metrics.f1_score(self.target_data, predicted_log))
        return model_log

    def train_extra_trees_classifier(self):
        # Build model
        model_et = sklearn.ensemble.ExtraTreesClassifier(n_estimators=50)
        model_et.fit(self.feature_df, self.target_data)

        # Assess model
        predicted_et = model_et.predict(self.feature_df)
        print(sklearn.metrics.classification_report(self.target_data, predicted_et))
        print(sklearn.metrics.f1_score(self.target_data, predicted_et))
        return model_et

    def train_decision_tree(self):
        # Build model
        model_dt = sklearn.tree.DecisionTreeClassifier(max_leaf_nodes=256, max_features=256)
        model_dt.fit(self.feature_df, self.target_data)

        # Assess model
        predicted_dt = model_dt.predict(self.feature_df)
        print(sklearn.metrics.classification_report(self.target_data, predicted_dt))
        print(sklearn.metrics.f1_score(self.target_data, predicted_dt))
        return model_dt

    @classmethod
    def dump_model_on_project_level(cls, model) -> None:
        """
        Pickles the model obtained in one of the methods:
        """
        from lexnlp.nlp.en.segments.sections import MODULE_PATH as SECTIONS_MODULE_PATH
        target_path = os.path.join(SECTIONS_MODULE_PATH, 'section_segmenter.pickle')
        joblib.dump(model, target_path)
        print(f'''File {target_path} is updated, size is
            {os.path.getsize(target_path)/1024/1024} MB''')

    @classmethod
    def _build_document_distribution(
            cls, text: str, characters=string.printable, norm=True):
        """
        Build document distribution based on fixed character and optionally norm to unit.
        """
        # Build character vector
        v = {}
        for c in characters:
            v["doc_char_{0}".format(c)] = text.count(c)
            v["doc_startchar_{0}".format(c)] = 0
        v["doc_startchar_other"] = 0

        # Build line start vector
        for line in text.splitlines():
            if len(line.strip()) > 0:
                c = line.strip()[0]

                if c in characters:
                    v["doc_startchar_{0}".format(c)] += 1
                else:
                    v["doc_startchar_other"] += 1
            else:
                continue

        # Norm if requested
        if norm:
            total_char = float(sum([b for a, b in v.items() if a.startswith("doc_char")]))
            total_startchar = float(sum([b for a, b in v.items() if a.startswith("doc_startchar")]))

            for k in v.keys():
                if k.startswith("doc_char"):
                    v[k] = v[k] / total_char
                elif k.startswith("doc_startchar"):
                    v[k] = v[k] / total_startchar

        return v

    def _build_section_break_features(
            self,
            lines,
            line_id,
            characters=string.printable,
            include_doc=None):
        """
        Build a feature vector for a given line ID with given parameters.
        """
        # Feature vector
        v = {}

        # Check start offset
        if line_id < self.line_window_pre:
            self.line_window_pre = line_id

        # Check final offset
        if (line_id + self.line_window_post) >= len(lines):
            self.line_window_post = len(lines) - self.line_window_post - 1

        # Iterate through window
        for i in range(-self.line_window_pre, self.line_window_post + 1):
            try:
                line = lines[line_id + i]
            except IndexError:
                continue

            # Count length
            v["line_len_{0}".format(i)] = len(line)
            v["line_lenstrip_{0}".format(i)] = len(line.strip())
            v["line_title_case_{0}".format(i)] = line == line.title()
            v["line_upper_case_{0}".format(i)] = line == line.upper()

            # Count characters
            v["line_n_alpha_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("L")])
            v["line_n_number_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("N")])
            v["line_n_punct_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("P")])
            v["line_n_whitespace_{0}".format(i)] = sum([1 for c in line if unicodedata.category(c).startswith("Z")])

        # Simple checks
        v["section"] = 1 if "section" in line else 0
        v["SECTION"] = 1 if "SECTION" in line else 0
        v["Section"] = 1 if "Section" in line else 0
        v["article"] = 1 if "article" in line else 0
        v["ARTICLE"] = 1 if "ARTICLE" in line else 0
        v["Article"] = 1 if "Article" in line else 0
        v["sw_section"] = 1 if line.strip().lower().startswith("section") else 0
        v["sw_article"] = 1 if line.strip().lower().startswith("article") else 0
        v["first_char_punct"] = (line.strip()[0] in string.punctuation) if len(line.strip()) > 0 else False
        v["last_char_punct"] = (line.strip()[-1] in string.punctuation) if len(line.strip()) > 0 else False
        v["first_char_number"] = (line.strip()[0] in string.digits) if len(line.strip()) > 0 else False
        v["last_char_number"] = (line.strip()[-1] in string.digits) if len(line.strip()) > 0 else False

        # Build character vector
        for c in characters:
            v["char_{0}".format(c)] = lines[line_id].count(c)

        # Add doc if requested
        if include_doc:
            v.update(include_doc)

        return v
