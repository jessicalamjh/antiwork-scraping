# NLP with Antiwork

## Reddit's r/antiwork

Update 2022-01-17

- Posts and comments scraped with [PSAW](https://psaw.readthedocs.io/en/latest)
- Notes
  - PMAW constantly warns that a few shards are down, thus retrieved data could be incomplete 
    - Currently looking up ways to ensure this does not happen
  - There are posts whose selftexts were not fully extracted, e.g. from [this post](https://www.reddit.com/r/antiwork/comments/eodidy/what_the_fuck_is_the_point_of_a_resume_when_the/), only the first sentence was retrieved
    - This may be a consequence of the shards issue

## TikTok's #antiwork

Update 2022-01-16

- Post metadata scraped with [github.com/drawrowfly/tiktok-scraper](https://github.com/drawrowfly/tiktok-scraper)
	- See /tiktok-sample for example outputs
	- Pros: quite fast (1 min for 1K posts), no rate limits, well documented and decently popular
- Notes
	- Unable to find any (free) existing way of scraping unlimited comments 
		- Possible option: implementing scraper myself, but that will take time to learn
	- Only 1.1K posts found under the #antiwork hashtag, which has 25M views
		- Oldest post is from 2020-04-01
		- Similar hashtags (#iquitmyjob, #iquit) have more views (resp. 40M, 442M) over ~1.8K posts
