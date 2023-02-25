# Imports
import glob
import sys
import tarfile

# Path setup
sys.path.append("/data/workspace/lexpredict-contraxsuite-core/")

# Packages
from lexnlp.nlp.en.segments.sentences import get_sentences
from lexnlp.nlp.en.tokens import get_stems

# Gensim
from gensim.models.word2vec import Word2Vec


def process_sentence(sentence: str):
    sentence_stems = [s for s in get_stems(sentence, stopword=True, lowercase=True) if s.isalpha()]
    return sentence_stems


if __name__ == "__main__":
    sentence_list = []

    for file_name in glob.glob("/data/workspace/lexpredict-contraxsuite-core/test_data/agreements-text.tar.gz"):
        print(file_name)
        with tarfile.open(file_name, "r:gz") as corpus_tar_file:
            member_list = corpus_tar_file.getmembers()[0:70000]
            num_members = len(member_list)

            # Iterate through all
            for i, tar_member in enumerate(member_list):
                # Output
                if i % 100 == 0:
                    print((file_name, i, float(i)/num_members * 100., tar_member.name, len(sentence_list)))

                # Read buffer
                member_file = corpus_tar_file.extractfile(tar_member.name)
                if member_file is None:
                    print((file_name, tar_member.name, "invalid file"))
                    continue
                member_buffer = member_file.read().decode("utf-8")
                if len(member_buffer.strip()) == 0:
                    continue

                # Parse into sentence data
                for sentence in get_sentences(member_buffer):
                    sentence_list.append(process_sentence(sentence))

    # Train w2v CBOW model
    for size in (50, 100, 200, 300, 500):
        for window in (5, 10, 20):
            w2v_model_cbow = Word2Vec(
                sentences=sentence_list,
                vector_size=size,
                window=window,
                min_count=10,
                workers=3,
            )
            w2v_model_cbow.save("models/w2v_cbow_all_size{0}_window{1}".format(size, window))
            print("cbow trained: size={0}, window={1}".format(size,  window))
