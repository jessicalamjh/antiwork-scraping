from datetime import datetime
import json
import os
import os.path as path
import shutil
from tqdm import tqdm

from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel
from gensim.models.phrases import Phrases

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
logs_dir = path.join(root_dir, f"logs/reddit")
outs_dir = path.join(root_dir, f"output/reddit")
posts_dir = path.join(root_dir, f"data/reddit/preprocessed/posts")

# misc prep
def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H%M")

###############################################################################
# LDA constants
MIN_LENGTH = 6 # ignore posts that contain <6 lemmas
NO_BELOW = 6   # ignore lemmas that appear in <6 posts
NO_ABOVE = 0.33 # ignore lemmas that appear in >33% of posts
MIN_N_TOPICS = 5 # min. number of latent topics
MAX_N_TOPICS = 8 # max. number of latent topics

# LDA functions
def process(texts, no_below=NO_BELOW, no_above=NO_ABOVE):
    print("Building phrased_texts, id2word, and word_ids")

    # create corpus of bigrams from input texts
    bigram_phraser = Phrases(texts)
    texts = [bigram_phraser[text] for text in texts]

    # create id2word and filter extremes
    id2word = Dictionary(texts)
    print(f"Size of original id2word: {len(id2word)}")

    id2word.filter_extremes(no_below=no_below, no_above=no_above)
    print(f"Size of filtered id2word: {len(id2word)}")

    # build BoW embeddings
    word_ids = [id2word.doc2bow(text) for text in texts]

    return texts, id2word, word_ids

def get_formatted_topics(lda_model):
    # format LDA topics for readability
    formatted_topics = []
    for _, topic in lda_model.show_topics():
        entries = []
        for entry in topic.split(" + "):
            score, word = entry.split("*")
            score = float(score)
            word = word.strip().replace("\"", '')
            entries.append((score, word))
        formatted_topics.append(entries)
    return formatted_topics

def validate(phrased_texts, id2word, word_ids, n_topics):
    # fit LDA model and coherence model
    lda_model = LdaModel(
        corpus=word_ids, 
        id2word=id2word,
        num_topics=n_topics,
        alpha='auto',
        eta='auto',
        random_state=1,
    )
    coherence_model = CoherenceModel(
        model=lda_model,
        texts=phrased_texts,
        dictionary=id2word,
        coherence='c_v',
    )

    # export LDA topics and coherence score
    result = {
        'num_topics': n_topics, 
        'coherence': coherence_model.get_coherence(), 
        'topics': get_formatted_topics(lda_model)
    }
    return result

###############################################################################
# run
if __name__ == '__main__':
    timestamp = get_timestamp()
    
    print("Loading preprocessed selftexts...")
    filenames = sorted(os.listdir(posts_dir))
    texts = []
    for filename in tqdm(filenames):
        filepath = path.join(posts_dir, filename)
        with open(filepath, 'r') as f:
            for line in f:
                x = json.loads(line)
                text = [lem for sent in x['filtered_lemmas'] for lem in sent]

                # only take entries with long enough text
                if len(text) >= MIN_LENGTH:
                    texts.append(text)
    print(f"Number of selftexts loaded: {len(texts)}")

    print(f"\nRunning preprocessing for LDA...")
    phrased_texts, id2word, word_ids = process(texts)

    # prepare output directory
    out_dir = path.join(outs_dir, f"LDA-{timestamp}")
    os.makedirs(out_dir)

    # export copy of this script for posterity
    out_path = path.join(out_dir, f"LDA-reddit.py-copy")
    shutil.copy(path.realpath(__file__), out_path)

    # export results of LDA
    print(f"\nRunning LDA with n_topics in [{MIN_N_TOPICS}, {MAX_N_TOPICS}]")
    out_path = path.join(out_dir, f"results.jsonl")
    f_out = open(out_path, 'w')
    for n_topics in tqdm(range(MIN_N_TOPICS, MAX_N_TOPICS+1)):
        result = validate(phrased_texts, id2word, word_ids, n_topics)
        print(json.dumps(result), file=f_out)
    f_out.close()

    print("Done.")