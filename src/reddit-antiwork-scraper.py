import argparse
from datetime import datetime, timedelta
import json
import os.path as path
import time

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
# output directory
output_dir = path.join(args.output_dir, args.mode)

# PSAW setup
api = PushshiftAPI()
if args.mode == "posts":
    searcher = api.search_submissions
else:
    searcher = api.search_comments

###############################################################################
# run
if __name__ == '__main__':
    
    # prepare timeframe
    start = [int(_) for _ in args.start.split("-")]
    end = [int(_) for _ in args.end.split("-")]
    start = datetime(*start)
    end = datetime(*end)
    
    for i in range((end - start).days):

        start_time = time.time()

        # prepare start and end of date
        date = start + timedelta(i)
        after = int(date.timestamp())
        before = int((date + timedelta(1)).timestamp())
        print(f"Currently on: {date.strftime('%Y-%m-%d')}")

        # export posts/comments made on this date
        outpath = path.join(
            output_dir, f"{date.strftime(format='%Y-%m-%d')}.jsonl")

        f_out = open(outpath, 'w')
        for entry in searcher(subreddit="antiwork", after=after, before=before):
            # out = make_json_formattable(entry)
            print(json.dumps(entry), file=f_out)
        f_out.close()

        print(f"Time taken: {time.time() - start_time}s\n")

    print("Done")
