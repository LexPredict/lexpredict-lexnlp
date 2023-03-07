# Imports
import glob
import tarfile
from typing import List

# Packages
from lexnlp.nlp.en.tokens import get_stems

# Gensim
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


def process_text(text: str) -> List[str]:
    return [
        stem for stem in get_stems(text, stopword=True, lowercase=True)
        if stem.isalpha()
    ]


if __name__ == "__main__":
    documents = []
    min_stem_count = 10

    for file_name in glob.glob("/data/workspace/lexpredict-contraxsuite-core/test_data/agreements-text.tar.gz"):
        print(file_name)
        with tarfile.open(file_name, "r:gz") as corpus_tar_file:
            member_list = corpus_tar_file.getmembers()[0:50000]
            num_members = len(member_list)

            # Iterate through all
            for i, tar_member in enumerate(member_list):
                # Output
                if i % 100 == 0:
                    print((file_name, i, float(i)/num_members * 100., tar_member.name, len(documents)))

                # Read buffer
                member_file = corpus_tar_file.extractfile(tar_member.name)
                if member_file is None:
                    print((file_name, tar_member.name, "invalid file"))
                    continue
                member_buffer = member_file.read().decode("utf-8")
                if len(member_buffer.strip()) == 0:
                    continue

                # Parse into sentence data
                try:
                    stems = process_text(member_buffer)
                    if len(stems) < min_stem_count:
                        continue
                    doc = TaggedDocument(stems, ["{0}".format(tar_member.name)])
                    documents.append(doc)                
                except Exception as e:
                    print(e)

    # Train w2v CBOW model
    for size in (50, 100, 200, 500):
        for window in (5, 10, 20):
            d2v_model = Doc2Vec(
                documents=documents,
                vector_size=size,
                window=window,
                min_count=10,
                workers=2,
            )
            d2v_model.save("models/d2v_all_size{0}_window{1}".format(size, window))
            print("d2v trained: size={0}, window={1}".format(size,  window))
