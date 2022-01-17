import argparse
from datetime import datetime, timedelta
import json
import os.path as path
from tqdm import tqdm
import warnings

from pmaw import PushshiftAPI

###############################################################################
# arguments
parser = argparse.ArgumentParser("PSAW scraper for r/antiwork")
parser.add_argument("--mode", choices=["posts", "comments"], help="Scrape either posts or comments")
parser.add_argument("--start", help="Start date for scraping (YYYY-MM-DD), inclusive")
parser.add_argument("--end", help="End date for scraping (YYYY-MM-DD), not inclusive")
parser.add_argument("--output-dir", help="Where to store scraped outputs")

args = parser.parse_args()

###############################################################################
# suppress shards warning
warnings.simplefilter("ignore")

# output directory
output_dir = path.join(args.output_dir, args.mode)

# PSAW setup
api = PushshiftAPI()
if args.mode == "posts":
    searcher = api.search_submissions
else:
    searcher = api.search_comments

# for easy export as JSONL file
ALLOWED_TYPES = set(
    [type(None), bool, int, float, str, tuple, list, dict, set])

def make_json_formattable(dictionary, allowed_types=ALLOWED_TYPES):
    out = dictionary.copy()
    for k, v in dictionary.items():

        # force unacceptable values to be strings
        if type(v) not in allowed_types:
            name = str(v)
            out[k] = name

            # delete values that cannot be coerced into strings
            if str(v) == repr(v): 
                del out[k]

    return out

###############################################################################
# run
if __name__ == '__main__':

    # prepare timeframe
    start = [int(_) for _ in args.start.split("-")]
    end = [int(_) for _ in args.end.split("-")]
    start = datetime(*start)
    end = datetime(*end)

    print(f"Scraping {args.mode} between {start} and {end} from r/antiwork")
    
    for i in tqdm(range((end - start).days)):

        # prepare start and end of date
        date = start + timedelta(i)
        after = int(date.timestamp())
        before = int((date + timedelta(1)).timestamp())

        # export posts/comments made on this date
        outpath = path.join(
            output_dir, f"{date.strftime(format='%Y-%m-%d')}.jsonl")

        f_out = open(outpath, 'w')
        for entry in searcher(subreddit="antiwork", after=after, before=before):
            out = make_json_formattable(entry)
            print(json.dumps(out), file=f_out)
        f_out.close()
