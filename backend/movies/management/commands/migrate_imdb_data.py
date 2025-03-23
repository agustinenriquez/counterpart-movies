import sqlite3

from django.core.management.base import BaseCommand
from movies.models import Movie, Name, Principal

# Path to your existing SQLite database
OLD_DB_PATH = "../imdb_subset.db"


class Command(BaseCommand):
    help = "Migrate IMDb data from an existing SQLite database"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting data migration...")
        self.stdout.write(f"Connecting to the old database at {OLD_DB_PATH}...")
        conn = sqlite3.connect(OLD_DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                tconst, titleType, primaryTitle, originalTitle, isAdult, startYear, endYear, runtimeMinutes, genres
            FROM movies
        """)
        movies = cursor.fetchall()
        for movie in movies:
            (
                tconst,
                title_type,
                primary_title,
                original_title,
                is_adult,
                start_year,
                end_year,
                runtime_minutes,
                genres,
            ) = movie
            Movie.objects.update_or_create(
                tconst=tconst,
                title_type=title_type,
                title=primary_title,
                original_title=original_title if original_title else None,
                is_adult=bool(int(is_adult)) if is_adult else False,
                year=start_year if start_year != "\\N" else None,
                end_year=end_year if end_year != "\\N" else None,
                runtime=runtime_minutes if runtime_minutes != "\\N" else None,
                genre=genres if genres != "\\N" else None,
            )
        self.stdout.write(f"Imported {len(movies)} movies.")

        cursor.execute("""
            SELECT
                nconst, primaryName, birthYear, deathYear, primaryProfession, knownForTitles
            FROM names
        """)
        names = cursor.fetchall()
        for name in names:
            (
                nconst,
                primary_name,
                birth_year,
                death_year,
                primary_professions,
                known_for_titles,
            ) = name
            Name.objects.update_or_create(
                nconst=nconst,
                name=primary_name,
                birth_year=birth_year if birth_year != "\\N" else None,
                death_year=death_year if death_year != "\\N" else None,
                primary_professions=primary_professions
                if primary_professions != "\\N"
                else None,
                known_for_titles=known_for_titles
                if known_for_titles != "\\N"
                else None,
            )
        self.stdout.write(f"Imported {len(names)} names.")

        cursor.execute("""
            SELECT
                tconst, nconst, category, job, characters
            FROM principals
        """)
        principals = cursor.fetchall()
        for principal in principals:
            tconst, nconst, category, job, characters = principal
            try:
                movie = Movie.objects.get(tconst=tconst)
                name = Name.objects.get(nconst=nconst)
                try:
                    Principal.objects.create(
                        tconst=movie,
                        nconst=name,
                        category=category if category else "unknown",
                        job=job if job != "\\N" else None,
                        characters=characters if characters != "\\N" else None,
                    )
                except Exception as e:
                    self.stderr.write(
                        f"Failed to import principal with tconst={tconst}, nconst={nconst}."
                    )
                    self.stderr.write(f"Error: {e}")
            except (Movie.DoesNotExist, Name.DoesNotExist):
                self.stdout.write(
                    f"Skipped principal with tconst={tconst}, nconst={nconst} due to missing reference."
                )
                continue
        self.stdout.write(f"Imported {len(principals)} principals.")

        conn.close()
        self.stdout.write("Data migration completed!")
