import argparse
import json
import os
import os.path as path

from gensim.corpora import Dictionary
from gensim.models import LdaModel, CoherenceModel
from gensim.models.phrases import Phrases

import utils

###############################################################################
# arguments
parser = argparse.ArgumentParser("Trains LDA on filtered, preprocessed reddit content for a range of possible n_topics.")
parser.add_argument("--mode", choices=["posts", "comments"], help="Run on either posts or comments.")
parser.add_argument("--min-n-chars", type=int, default=3, help="Min. number of characters per lemma.")
parser.add_argument("--min-n-lemmas", type=int, default=6, help="Min. number of lemmas per content.")
parser.add_argument("--no-below", type=int, default=6, help="Min. number of contents that must contain a lemma for the lemma to be included.")
parser.add_argument("--no-above", type=float, default=0.33, help="Max. fraction of contents that is allowed to contain a lemma for the lemma to be considered.")
parser.add_argument("--min-n-topics", type=int, default=5, help="Min. number of latent topics.")
parser.add_argument("--max-n-topics", type=int, default=30, help="Max. number of latent topics.")

args = parser.parse_args()

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
preprocessed_dir = path.join(root_dir, "data/reddit/preprocessed")
outs_dir = path.join(root_dir, f"output/reddit")

# misc prep
if args.mode == 'posts':
    text_key = 'selftext'
else:
    text_key = 'body'

###############################################################################
# functions
def process(texts):
    # create corpus of bigrams from input texts
    bigram_phraser = Phrases(texts)
    phrased_texts = [bigram_phraser[text] for text in texts]

    # create id2word and filter extremes
    id2word = Dictionary(phrased_texts)
    print(f"Size of original id2word: {len(id2word)}")

    id2word.filter_extremes(no_below=args.no_below, no_above=args.no_above)
    print(f"Size of filtered id2word: {len(id2word)}\n")

    # build BoW embeddings
    word_ids = [id2word.doc2bow(text) for text in phrased_texts]

    return phrased_texts, id2word, word_ids

def get_topics(lda_model, n_topics):
    # returns LDA topics as a nested list (one inner list per topic)
    
    topics = []
    for _, topic_string in lda_model.show_topics(num_topics=n_topics):
        
        # convert each topic string to a list of (score, word)
        topic = []
        for entry in topic_string.split(" + "):
            score, word = entry.split("*")
            word = word.strip().replace("\"", '')
            topic.append((float(score), word))
        topics.append(topic)
        
    return topics
    
def run_LDA(phrased_texts, id2word, word_ids, n_topics):
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

    # return LDA topics and coherence score
    result = {
        'n_topics': n_topics, 
        'coherence': coherence_model.get_coherence(), 
        'topics': get_topics(lda_model, n_topics)
    }
    return result

###############################################################################
# run
if __name__ == '__main__':
    timestamp = utils.get_timestamp()
    
    print(f"Running LDA with {args.min_n_topics}, ..., {args.max_n_topics} n_topics.")
    print(f"Timestamp: {timestamp}\n")
    
    # load preprocessed data (skip short contents)
    filepath = path.join(preprocessed_dir, f"{args.mode}.jsonl")
    texts = []
    with open(filepath, 'r') as f:
        for line in f:
            x = json.loads(line)
            text = [
                lem for sent in x[f'filtered_lemmatized_{text_key}'] 
                for lem in sent if len(lem) >= args.min_n_chars]
            if len(text) >= args.min_n_lemmas:
                texts.append(text)
    print(f"Number of contents loaded: {len(texts)}.")

    print(f"Building bigrams, id2word, and word_ids for LDA.")
    phrased_texts, id2word, word_ids = process(texts)

    # prepare output directory
    out_dir = path.join(outs_dir, f"LDA-{timestamp}")
    os.makedirs(out_dir)

    # save copy of input args
    args_path = path.join(out_dir, "args.json")
    with open(args_path, 'w') as f_out:
        json.dump(args.__dict__, f_out, indent=2)

    # prepare output paths
    LDA_results_path = path.join(out_dir, f"results.jsonl")
    topics_path = path.join(out_dir, f"prettytopics.txt")
    
    # run LDA over range of n_topics values
    with open(LDA_results_path, 'w') as f_lda, open(topics_path, 'w') as f_topics:
        
        for n_topics in range(args.min_n_topics, args.max_n_topics+1):
            result = run_LDA(phrased_texts, id2word, word_ids, n_topics)
            
            # export json results
            print(json.dumps(result), file=f_lda)
            
            # export readable results
            print(f"\nn_topics = {len(result['topics'])}", file=f_topics) 
            for topic in result['topics']:
                print(f"- {' '.join([w for _, w in topic])}", file=f_topics)
                
            print(f"Done with n_topics={n_topics}.")
    print("Done.")