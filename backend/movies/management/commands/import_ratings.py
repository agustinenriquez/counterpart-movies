import csv
import gzip
import logging
import os
from decimal import Decimal

import requests
from django.core.management.base import BaseCommand
from movies.models import Movie, Rating
from tqdm import tqdm

logger = logging.getLogger(__name__)

IMDB_RATINGS_GZ_URL = "https://datasets.imdbws.com/title.ratings.tsv.gz"
LOCAL_UNCOMPRESSED = "title.ratings.tsv"  # local uncompressed file


class Command(BaseCommand):
    """
    Downloads 'title.ratings.tsv.gz' from IMDb, decompresses to 'title.ratings.tsv'
    if not already present, and imports ratings for existing Movies.
    """

    help = "Fetches compressed 'title.ratings.tsv.gz' from IMDb, writes 'title.ratings.tsv' uncompressed, and imports data."

    def handle(self, *args, **options):
        self.stdout.write(f"Checking for local '{LOCAL_UNCOMPRESSED}' file.")
        logger.info("Starting IMDb ratings import process...")

        try:
            if os.path.exists(LOCAL_UNCOMPRESSED):
                # We already have an uncompressed file; skip re-download
                self.stdout.write(
                    f"File '{LOCAL_UNCOMPRESSED}' already exists. Skipping download."
                )
                logger.info("Skipping download; file already present.")
            else:
                # 1) Download the gzipped file
                gz_filename = "title.ratings.tsv.gz"
                self.stdout.write(f"Downloading from {IMDB_RATINGS_GZ_URL}...")
                logger.info("Downloading from %s", IMDB_RATINGS_GZ_URL)
                response = requests.get(IMDB_RATINGS_GZ_URL, stream=True)
                response.raise_for_status()

                with open(gz_filename, "wb") as gz_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            gz_file.write(chunk)

                self.stdout.write(f"Downloaded '{gz_filename}'. Now decompressing...")

                # 2) Decompress local .gz -> local uncompressed
                with open(gz_filename, "rb") as gz_in:
                    with gzip.GzipFile(fileobj=gz_in) as gz_file:
                        with open(LOCAL_UNCOMPRESSED, "wb") as tsv_out:
                            for line in gz_file:
                                tsv_out.write(line)

                # (Optional) Remove the .gz file if you don't need it
                os.remove(gz_filename)
                self.stdout.write(
                    f"Decompressed to '{LOCAL_UNCOMPRESSED}' and removed '{gz_filename}'."
                )

            # 3) Parse local uncompressed file
            count = 0
            if os.path.exists(LOCAL_UNCOMPRESSED):
                self.stdout.write(f"Parsing '{LOCAL_UNCOMPRESSED}' for import...")
                with open(LOCAL_UNCOMPRESSED, encoding="utf-8") as tsv_file:
                    reader = csv.DictReader(tsv_file, delimiter="\t")
                    # Expected columns: tconst, averageRating, numVotes

                    for row in tqdm(reader, desc="Importing IMDb ratings"):
                        tconst = row["tconst"]
                        avg = row["averageRating"]
                        votes = row["numVotes"]

                        # Only update if matching Movie is in DB
                        try:
                            movie = Movie.objects.get(tconst=tconst)
                        except Movie.DoesNotExist:
                            logger.info(
                                "Skipping rating for non-existent Movie '%s'.", tconst
                            )
                            continue

                        try:
                            avg = Decimal(avg)
                            votes = int(votes)
                        except ValueError:
                            # Skip if rating/votes are not valid numbers
                            continue

                        try:
                            Rating.objects.update_or_create(
                                tconst=movie,
                                defaults={"average_rating": avg, "num_votes": votes},
                            )
                            count += 1
                        except Exception as e:
                            logger.exception("Failed to import rating record.")
                            self.stderr.write(self.style.ERROR(f"Error: {e}"))
            else:
                self.stderr.write(
                    self.style.ERROR(
                        f"Error: '{LOCAL_UNCOMPRESSED}' file not found for import."
                    )
                )
                logger.error("File '%s' not found for import.", LOCAL_UNCOMPRESSED)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Imported/updated {count} rating records from IMDb."
                )
            )
            logger.info("Successfully imported/updated %d rating records.", count)

        except Exception as e:
            logger.exception("Failed to import IMDb ratings.")
            self.stderr.write(self.style.ERROR(f"Error: {e}"))
