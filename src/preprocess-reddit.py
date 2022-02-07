import argparse
import json
import os
import os.path as path
import re
from tqdm import tqdm

import spacy

###############################################################################
# arguments
parser = argparse.ArgumentParser("Preprocessing of reddit content")
parser.add_argument("--mode", choices=["posts", "comments"], help="Preprocess either posts or comments")

args = parser.parse_args()

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
filtered_dir = path.join(root_dir, f"data/reddit/filtered/{args.mode}")
preprocessed_dir = path.join(root_dir, f"data/reddit/preprocessed/{args.mode}")

# misc prep
nlp = spacy.load('en_core_web_sm')
if args.mode == 'posts':
    key = 'selftext'
else:
    key = 'body'

###############################################################################
# run
def preprocess(x, key=key):
    doc = nlp(x[key]) # run spacy model

    tokens = [] # list of list of lowercased tokens
    lemmas = [] # list of list of lemmatized tokens
    filtered_lemmas = [] # same as lemmas, but no stopwords and non-letters

    for sent in doc.sents:
        # get lists of tokens/lemmas/filtered lemmas in sentence
        sent_tokens = [tok.text.lower() for tok in sent]
        sent_lemmas = [tok.lemma_.lower() for tok in sent]
        filtered_sent_lemmas = [
            tok.lemma_.lower() for tok in sent 
            if tok.is_alpha and not tok.is_stop]

        # skip empty entries
        tokens.append([tok for tok in sent_tokens if tok])
        lemmas.append([lem for lem in sent_lemmas if lem])
        filtered_lemmas.append([lem for lem in filtered_sent_lemmas if lem])

    # remove any empty sentences
    out = x.copy()
    out['tokens'] = [sent for sent in tokens if sent]
    out['lemmas'] = [sent for sent in lemmas if sent]
    out['filtered_lemmas'] = [sent for sent in filtered_lemmas if sent]
    
    return out

if __name__ == '__main__':

    # get list of all filtered data
    filenames = sorted(os.listdir(filtered_dir))

    for filename in tqdm(filenames):

        # prepare in/out paths
        filepath = path.join(filtered_dir, filename)
        out_path = path.join(preprocessed_dir, filename)

        # preprocess each entry and export
        with open(filepath, 'r') as f, open(out_path, 'w') as f_out:
            for line in f:
                x = json.loads(line)
                x = preprocess(x)
                print(json.dumps(x), file=f_out)