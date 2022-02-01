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

args = parser.parse_args()

###############################################################################
# directories
root_dir = path.dirname(path.dirname(__file__))
data_dir = path.join(root_dir, f"data/reddit/original/{args.mode}")
logs_dir = path.join(root_dir, f"logs/reddit/{args.mode}")

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

        # get date to be scraped
        date = start + timedelta(i)
        prettydate = date.strftime(format='%Y-%m-%d')

        # prepare log and out paths
        log_path = path.join(logs_dir, f"{prettydate}.log")
        out_path = path.join(
            data_dir, f"{date.strftime(format='%Y-%m-%d')}.jsonl")

        # if log exists, shard metadata was good, and scraped output is nonempty, then continue to next date
        try:
            with open(log_path, 'r') as f_log:
                x = json.load(f_log)
            shard_data = x['shard_data']
            assert shard_data['successful'] == shard_data['total']
            assert path.getsize(out_path) != 0
            continue
        except:
            print(f"{prettydate} will be re-scraped")

        # get data from api with appropriate mode
        api = PushshiftAPI()
        if args.mode == "posts":
            searcher = api.search_submissions
        else:
            searcher = api.search_comments

        data = searcher(
            subreddit="antiwork", 
            after=int(date.timestamp()), 
            before=int((date + timedelta(1)).timestamp()))

        # if shard metadata is not available, skip to next date
        if api.metadata_.get('shards') is None:
            continue

        # export scraped data and metadata log
        with open(log_path, 'w') as f_log, open(out_path, 'w') as f_out:
            for entry in data:
                print(json.dumps(entry), file=f_out)

            log = {
                'mode': args.mode,
                'date_scraped': prettydate,
                'run_date': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'shard_data': api.metadata_.get('shards'),
                'time_taken': f"{time.time() - start_time:.3}s"
            }
            json.dump(log, fp=f_log)