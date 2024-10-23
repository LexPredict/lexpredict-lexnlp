[![Build Status](https://travis-ci.org/LexPredict/lexpredict-lexnlp.svg?branch=master)](https://travis-ci.org/LexPredict/lexpredict-lexnlp) [![Coverage Status](https://coveralls.io/repos/github/LexPredict/lexpredict-lexnlp/badge.svg?branch=master)](https://coveralls.io/github/LexPredict/lexpredict-lexnlp?branch=0.1.8) [![](https://tokei.rs/b1/github/lexpredict/lexpredict-lexnlp?category=code)](https://github.com/lexpredict/lexpredict-lexnlp) [![Docs](https://readthedocs.org/projects/lexpredict-lexnlp/badge/?version=docs-0.1.6)](http://lexpredict-lexnlp.readthedocs.io/en/docs-0.1.6/)

# LexNLP by LexPredict - ARM-specific readme
## Information retrieval and extraction for real, unstructured legal text
LexNLP is a library for working with real, unstructured legal text, including contracts, plans, policies, procedures,
and other material.
## LexNLP provides functionality such as:
* Segmentation and tokenization, such as
    * A sentence parser that is aware of common legal abbreviations like LLC. or F.3d.
    * Pre-trained segmentation models for legal concepts such as pages or sections.
* Pre-trained word embedding and topic models, broadly and for specific practice areas
* Pre-trained classifiers for document type and clause type
* Broad range of fact extraction, such as:
    * Monetary amounts, non-monetary amounts, percentages, ratios
    * Conditional statements and constraints, like "less than" or "later than"
    * Dates, recurring dates, and durations
    * Courts, regulations, and citations
* Tools for building new clustering and classification methods
* Hundreds of unit tests from real legal documents

![Logo](https://s3.amazonaws.com/lexpredict.com-marketing/graphics/lexpredict_lexnlp_logo_horizontal_1.png)

# Information
* ContraxSuite: https://contraxsuite.com/
* LexPredict: https://lexpredict.com/
* Official Website: https://lexnlp.com/
* Documentation: http://lexpredict-lexnlp.readthedocs.io/en/latest/ (in progress)
* Contact: support@contraxsuite.com

## Licensing
LexNLP is available under a dual-licensing model.  By default, this library can be used under AGPLv3 terms as detailed
in the repository LICENSE file; however, organizations can request a release from the AGPL terms or a non-GPL
evaluation license
by contacting ContraxSuite Licensing at <<license@contraxsuite.com>>.

## Requirements for `arm64`/Mac M1
* Python 3.12
* pipenv
* conda

## Installation on `arm64`/Mac M1

Some of the required packages (especially those related to `scikit-learn`) will fail to build wheels when `LexNLP` is installed on a M1 Mac.
For the package to be installed successfully, you can either use pre-compiled packages, or install a version of `scikit-learn` from the `conda-forge` installation that contains a C/C++ compiler (you can use [miniforge](https://github.com/conda-forge/miniforge#miniforge)). You can find the pre-compiled packages in [this](https://github.com/coaxsoft/arm_python_packages/tree/master/wheels) repo.

As of October 23, 2024, `scikit-learn` has native support of ARM. However, the issue persisted until I created a conda environment with the steps below.

Furthermore, LexNLP's dependencies are strict and lead to failed installation. This repo contains modified versions of `setup.py` and `python-requirements.txt` that (hopefully) will address this problem. WARNING: I have only tested extensively scripts related to definitions. The new installation instructions may end up breaking other LexNLP functions.

### Environment setup

Download this directory (don't install it yet). Move the directory to wherever you prefer. Create a new virtual environment w/ `scikit-learn` specified:
        
        conda create -n myenv -c conda-forge scikit-learn

where `myenv` is your environment name. 

Activate the environment and install pip into this environment: 

        conda activate myenv
        conda install pip

Navigate to the downloaded source directory and run

        pip install .

which executes the modified `setup.py` using the requirements we just copied over. 

This should successfully install the package. You may have to downgrade `setuptools` to ~=70.0.0.
