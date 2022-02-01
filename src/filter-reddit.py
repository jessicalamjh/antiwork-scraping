import argparse
import json
import os
import os.path as path
from tqdm import tqdm

###############################################################################
# arguments
parser = argparse.ArgumentParser("Preprocessing of reddit content")
parser.add_argument("--mode", choices=["posts", "comments"], help="Preprocess either posts or comments")

args = parser.parse_args()

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
original_dir = path.join(root_dir, f"data/reddit/original/{args.mode}")
filtered_dir = path.join(root_dir, f"data/reddit/filtered/{args.mode}")

###############################################################################
# run
def is_valid(x, mode=args.mode):
    # ignore content that is either deleted/removed or just empty strings
    if mode == 'posts':
        not_deleted = 'removed_by_category' not in x.keys() 
        has_text = 'selftext' in x.keys() and len(x['selftext']) > 0
        return not_deleted and has_text
    else:
        has_text = 'body' in x.keys() and len(x['body']) > 0 and x['body'] not in ['[removed]', '[deleted]']
        return has_text

if __name__ == '__main__':

    # get list of all scraped data
    filenames = os.listdir(original_dir)

    for filename in tqdm(filenames):

        # prepare in/out paths
        filepath = path.join(original_dir, filename)
        out_path = path.join(filtered_dir, filename)

        # export data that has text to out_path
        with open(filepath, 'r') as f, open(out_path, 'w') as f_out:
            for line in f:
                x = json.loads(line)
                if is_valid(x):
                    print(line.strip(), file=f_out)
