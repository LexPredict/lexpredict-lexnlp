# Imports
import html_text

import tarfile
import zlib

# NLP/ML imports
import spacy
from gensim.models.word2vec import Word2Vec

# Load spacy english
nlp = spacy.load('en')


def extract_sentences(text):
    sentence_list = []
    
    # Create spacy document
    doc = nlp(text)
    for sentence in doc.sents:
        sentence_list.append([t.lemma_ for t in sentence if t.lemma_.isalnum()])

    return sentence_list


if __name__ == "__main__":
    # Setup file
    for year in range(2016, 2018):
        print("parsing {0}...".format(year))
        
        # Get file name and open
        file_name = "data/filings_10k_{0}.tar.gz".format(year)
        tar_file = tarfile.open(file_name)
        print("opened tar.")
            
        # Sample data
        sample_sentence_list = []

        # Iterate through members
        j = 0
        
        print("building sample...")
        for tar_member in tar_file.getmembers():
            if j % 1000 == 0:
                print((year, j, len(sample_sentence_list)))

            j += 1
            # Skip non-files
            if not tar_member.isfile():
                continue

            # Parse real files
            try:
                # Read tar data
                member_buffer = zlib.decompress(tar_file.extractfile(tar_member).read()).decode("utf-8")

                if "<span" in member_buffer.lower() or "<p" in member_buffer.lower() or "<div" in member_buffer.lower():
                    filing_buffer = html_text.extract_text(member_buffer)
                else:
                    filing_buffer = member_buffer

                # Parse
                print((tar_member, len(member_buffer), len(filing_buffer), len(sample_sentence_list)))

                # Get sentence list
                sample_sentence_list.extend(extract_sentences(filing_buffer))

            except Exception as e:
                print(e)

        print("training w2v models...")
        # Train w2v CBOW model
        w2v_model_cbow = Word2Vec(sentences=sample_sentence_list, vector_size=200, window=20, min_count=10, workers=2)
        w2v_model_cbow.save("w2v_model_cbow_{0}".format(year))
        print("cbow trained.")

        # Train w2v SG model
        w2v_model_sg = Word2Vec(sentences=sample_sentence_list, vector_size=200, window=20, min_count=10, workers=2, sg=1)
        w2v_model_sg.save("w2v_model_sg_{0}".format(year))
        print("sg trained.")
