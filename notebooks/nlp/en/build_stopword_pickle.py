# Imports
import tarfile
import pandas
import pickle

# Sklearn imports
import nltk
import nltk.collocations

# LexNLP imports
import lexnlp.nlp.en.segments.sentences
import lexnlp.nlp.en.tokens

# Setup default path for documents
tar_input_path = "agreements-text.tar.gz"

# Store tokens
tokens = []

# Set sample size in docs
num_samples = 100
cutoff_amount = 0.5

if __name__ == "__main__":
    # Open tar
    with tarfile.open(tar_input_path, "r:gz") as corpus_tar_file:
        # Get list of files
        member_list = corpus_tar_file.getmembers()[0:num_samples]
        num_members = len(member_list)

        # Iterate through all
        for i, tar_member in enumerate(member_list):
            # Output
            if i % 100 == 0:
                print((tar_input_path, i, float(i)/num_members * 100., tar_member.name, len(member_list)))

            # Read buffer
            member_file = corpus_tar_file.extractfile(tar_member.name)
            if member_file is None:
                print((tar_input_path, tar_member.name, "invalid file"))
                continue
            member_buffer = member_file.read().decode("utf-8")
            if len(member_buffer.strip()) == 0:
                continue

            # Parse into sentence data
            try:
                tokens.extend(lexnlp.nlp.en.tokens.get_token_list(member_buffer, lowercase=True))
            except Exception as e:
                print(e)
                continue
    
    # Setup stopwords from corpus
    stopwords = set(list(nltk.corpus.stopwords.words("english")))
    token_counts = [(t, tokens.count(t)) for t in set(tokens)]
    
    # Build frequency DF
    all_token_count = pandas.DataFrame(token_counts, columns=["token", "count"])\
        .sort_values("count", ascending=False)\
        .reset_index()
    
    # Get cutoff
    cumulative_count = (all_token_count["count"].expanding().sum() / all_token_count["count"].sum())
    cutoff_index = (cumulative_count > cutoff_amount).argmax()
    
    # Update stopwords
    stopwords.update(all_token_count.iloc[0:cutoff_index].loc[:, "token"].tolist())
    
    # Serialize
    print("Total stopwords: {0}".format(len(stopwords)))

    # Save the tokenizer
    with open("stopwords.pickle", "wb") as out_file:
        pickle.dump(stopwords, out_file)
    