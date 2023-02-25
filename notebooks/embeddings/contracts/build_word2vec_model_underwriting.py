# Imports
import sys
import tarfile

# Path setup
sys.path.append("/data/workspace/lexpredict-contraxsuite-core/")

# Packages
from lexnlp.nlp.en.segments import get_sentences, get_paragraphs, get_pages
from lexnlp.nlp.en.tokens import get_stem_generator, get_stems

# Gensim
from gensim.models.word2vec import Word2Vec

def process_sentence(sentence):
    sentence_stems = [s for s in get_stems(sentence, stopword=True, lowercase=True) if s.isalpha()]
    return sentence_stems

if __name__ == "__main__":
    sentence_list = []

    with tarfile.open("/data/workspace/lexpredict-contraxsuite-core/test_data/underwriting_agreement.tar.gz", "r:gz") as corpus_tar_file:
        member_list = corpus_tar_file.getmembers()
        num_members = len(member_list)

        # Iterate through all
        for i, tar_member in enumerate(member_list):
            # Output
            if i % 100 == 0:
                print((i, float(i)/num_members * 100., tar_member.name, len(sentence_list)))

            # Read buffer
            member_buffer = corpus_tar_file.extractfile(tar_member.name).read().decode("utf-8")
            if len(member_buffer.strip()) == 0:
                continue

            # Parse into sentence data
            for sentence in get_sentences(member_buffer):
                sentence_list.append(process_sentence(sentence))

    # Train w2v CBOW model
    w2v_model_cbow = Word2Vec(
        sentences=sentence_list,
        vector_size=200,
        window=10,
        min_count=len(sentence_list)*0.001,
        workers=2,
    )
    w2v_model_cbow.save("models/w2v_cbow_underwriting_size200_window10")
    print("cbow trained.")
