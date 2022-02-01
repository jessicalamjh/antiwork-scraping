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
def preprocess(text):
    doc = nlp(text)

    full_lemmas = [] # list of list of lemmas
    filtered_lemmas = [] # same as full_lemmas, but without stopwords

    for sent in doc.sents:
        # lemmatize, lowercase, and remove any non-alphabetical characters
        lemmas = [re.sub(r"[^a-z]", "", tok.lemma_.lower()) for tok in sent]

        # remove lemmas that are empty strings
        full_lemmas.append([lem for lem in lemmas if len(lem) > 0])

        # remove any stopwords
        filtered_lemmas.append([
            lem for lem, tok in zip(lemmas, sent) 
            if len(lem) > 0 and not tok.is_stop])

    # remove any empty sentences 
    full_lemmas = [sent for sent in full_lemmas if sent]
    filtered_lemmas = [sent for sent in filtered_lemmas if sent]
    
    return full_lemmas, filtered_lemmas

if __name__ == '__main__':

    # get list of all filtered data
    filenames = os.listdir(filtered_dir)

    for filename in tqdm(filenames):

        # prepare in/out paths
        filepath = path.join(filtered_dir, filename)
        out_path = path.join(preprocessed_dir, filename)

        with open(filepath, 'r') as f, open(out_path, 'w') as f_out:
            for line in f:
                x = json.loads(line)

                # preprocess text into list of list of lemmas (two versions)
                full_lemmas, filtered_lemmas = preprocess(x[key])

                # export only if lemmatized text is nonempty
                if full_lemmas:
                    x[f'lemmatized_{key}'] = full_lemmas
                    x[f'filtered_lemmatized_{key}'] = filtered_lemmas

                    print(json.dumps(x), file=f_out)