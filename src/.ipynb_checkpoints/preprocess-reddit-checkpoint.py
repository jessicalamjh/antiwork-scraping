import argparse
import json
import os
import os.path as path

import re
import spacy

import utils

###############################################################################
# arguments
parser = argparse.ArgumentParser("Filters out non-textual reddit content and preprocesses for NLP.")
parser.add_argument("--mode", choices=["posts", "comments"], help="Run on either posts or comments.")

args = parser.parse_args()

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
data_dir = path.join(root_dir, "data/reddit")
original_dir = path.join(data_dir, f"original/{args.mode}")
preprocessed_dir = path.join(data_dir, f"preprocessed")

# misc prep
if args.mode == 'posts':
    text_key = 'selftext'
else:
    text_key = 'body'
    
nlp = spacy.load('en_core_web_lg')
    
###############################################################################
# functions
def is_valid(x):
    # content is valid <=> content contains text and is not deleted/removed
    has_text = text_key in x.keys() and len(x[text_key].strip()) > 0
    is_deleted = ('removed_by_category' in x.keys() 
                  or x[text_key] in ['[removed]', '[deleted]'])
        
    return has_text and not is_deleted
    
def preprocess(x):

    tokens = [] # list of list of lowercased tokens
    lemmas = [] # list of list of lemmatized tokens
    filtered_lemmas = [] # same as lemmas, but no stopwords and non-letters

    doc = nlp(x[text_key]) # run spacy model
    for sent in doc.sents:
        
        # get lists of tokens/lemmas/filtered lemmas in sentence
        sent_tokens = [tok.text.lower() for tok in sent]
        sent_lemmas = [tok.lemma_.lower() for tok in sent]
        filtered_sent_lemmas = [
            tok.lemma_.lower() for tok in sent if not tok.is_stop]
        filtered_sent_lemmas = [
            tok for tok in filtered_sent_lemmas 
            if re.search('[^a-z]', tok.lemma_.lower()) is None]

        # skip empty entries
        tokens.append([tok for tok in sent_tokens if tok])
        lemmas.append([lem for lem in sent_lemmas if lem])
        filtered_lemmas.append([lem for lem in filtered_sent_lemmas if lem])

    # remove any empty sentences
    out = x.copy()
    out[f'tokenized_{text_key}'] = [sent for sent in tokens if sent]
    out[f'lemmatized_{text_key}'] = [sent for sent in lemmas if sent]
    out[f'filtered_lemmatized_{text_key}'] = [
        sent for sent in filtered_lemmas if sent]
    
    return out

###############################################################################
# run
if __name__ == '__main__':
    print(f"Filtering and preprocessing reddit {args.mode}.")
    print(f"Timestamp: {utils.get_timestamp()}\n")
    
    # prepare path for preprocessed data
    out_path = path.join(preprocessed_dir, f"{args.mode}.jsonl")
    with open(out_path, 'w') as f_out:

        # get paths to original data (each file contains data for one day)
        filepaths = [
            path.join(original_dir, fname) 
            for fname in sorted(os.listdir(original_dir))]
        
        # load each day's data, filter out invalid content, and preprocess
        for filepath in filepaths:
            with open(filepath, 'r') as f:
                for line in f:
                    x = json.loads(line)
                    if is_valid(x):
                        x = preprocess(x)
                        print(json.dumps(x), file=f_out)
            print(f"Done with {filepath}.")
    print("Done.")
