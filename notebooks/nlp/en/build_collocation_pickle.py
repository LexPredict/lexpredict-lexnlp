# Imports
import itertools
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
bigrams = []

# Set sample size in docs
num_samples = 1000

# Set parameters
cutoff_amount = 0.5
top_n_list = [100, 1000, 10000]
min_freq = 100

if __name__ == "__main__":
    # Set number of samples
    num_samples = 10000

    # Initialize frequency distributions
    token_fd = nltk.FreqDist()
    wildcard_fd = nltk.FreqDist()
    bigram_fd = nltk.FreqDist()
    trigram_fd = nltk.FreqDist()

    # Iterate through files
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
                    for sentence in lexnlp.nlp.en.segments.sentences.get_sentence_list(member_buffer):
                        sentence_tokens = lexnlp.nlp.en.tokens.get_token_list(sentence, lowercase=True)
                        sentence_tokens = [t for t in sentence_tokens if t.isalpha()]

                        for window in nltk.ngrams(sentence_tokens, 3, pad_right=True):
                            w1 = window[0]
                            for w2, w3 in itertools.combinations(window[1:], 2):
                                token_fd[w1] += 1
                                if w2 is None:
                                    continue
                                bigram_fd[(w1, w2)] += 1
                                if w3 is None:
                                    continue
                                wildcard_fd[(w1, w3)] += 1
                                trigram_fd[(w1, w2, w3)] += 1
                                
                except Exception as e:
                    print(e)
                    continue
    
    # Create measure objects
    bigram_measures = nltk.collocations.BigramAssocMeasures()
    trigram_measures = nltk.collocations.TrigramAssocMeasures()

    for n in top_n_list:
        # Apply filter and output
        bigram_finder = nltk.collocations.BigramCollocationFinder(token_fd, bigram_fd)
        bigram_finder.apply_freq_filter(min_freq)
        bigram_collocations = list(bigram_finder.nbest(bigram_measures.pmi, n))
        print((n, len(bigram_collocations), bigram_collocations[-1]))

        # Save the tokenizer
        with open("collocation_bigrams_{0}.pickle".format(n), "wb") as out_file:
            pickle.dump(bigram_collocations, out_file)

        # Apply filter and output
        trigram_finder = nltk.collocations.TrigramCollocationFinder(token_fd, bigram_fd, wildcard_fd, trigram_fd)
        trigram_finder.apply_freq_filter(min_freq)
        trigram_collocations = list(trigram_finder.nbest(trigram_measures.pmi, n))
        print((n, len(trigram_collocations), trigram_collocations[-1]))

        # Save the tokenizer
        with open("collocation_trigrams_{0}.pickle".format(n), "wb") as out_file:
            pickle.dump(trigram_collocations, out_file)