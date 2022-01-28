import argparse
from datetime import datetime, timedelta
import json
import os.path as path
import sys
import time

import contextlib, io

from pmaw import PushshiftAPI

###############################################################################
# arguments
parser = argparse.ArgumentParser("PSAW scraper for r/antiwork")
parser.add_argument("--mode", choices=["posts", "comments"], help="Scrape either posts or comments")
parser.add_argument("--start", help="Start date for scraping (YYYY-MM-DD), inclusive")
parser.add_argument("--end", help="End date for scraping (YYYY-MM-DD), not inclusive")
parser.add_argument("--outs-dir", help="Path to folder for scraped data")
parser.add_argument("--logs-dir", help="Path to folder for scraping logs")

args = parser.parse_args()

###############################################################################
# run
if __name__ == '__main__':
    
    # prepare timeframe
    start = [int(_) for _ in args.start.split("-")]
    end = [int(_) for _ in args.end.split("-")]
    start = datetime(*start)
    end = datetime(*end)
    
    # main loop
    for i in range((end - start).days):
        start_time = time.time()

        date = start + timedelta(i)
        prettydate = date.strftime(format='%Y-%m-%d')

        # prepare scraping api
        api = PushshiftAPI()
        if args.mode == "posts":
            searcher = api.search_submissions
        else:
            searcher = api.search_comments

        # prepare log and out paths
        log_path = path.join(
            args.logs_dir, args.mode, f"{prettydate}.log")
        out_path = path.join(
            args.outs_dir, args.mode, 
            f"{date.strftime(format='%Y-%m-%d')}.jsonl")


        with open(log_path, 'w') as f_log, open(out_path, 'w') as f_out:
            with contextlib.redirect_stdout(f_log):
                data = searcher(
                    subreddit="antiwork", 
                    after=int(date.timestamp()), 
                    before=int((date + timedelta(1)).timestamp()))

                print(f"Scraping {args.mode} made on {prettydate}")
                print(f"Scraped on: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                print(f"Shards: {api.metadata_.get('shards')}")

                for entry in data:
                    print(json.dumps(entry), file=f_out)

                print(f"Time taken: {time.time() - start_time:.3}s")