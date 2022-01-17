#!/bin/bash
	
if [ -z $1 ]; then
	echo "Desired output directory is missing."
elif [ -z $2 ]; then
	echo "Number of posts to scrape is missing."
else
	TIMESTAMP=$(date +"%Y-%m-%d_%H%M")
	OUTPUT_DIR="$1/$TIMESTAMP"
	echo "Scraped output is saved to: $OUTPUT_DIR"
	echo "Number to scrape: $2"

	mkdir $OUTPUT_DIR
	docker run --rm -v $OUTPUT_DIR:/usr/app/files tiktok-scraper hashtag antiwork -t json -n $2
fi



