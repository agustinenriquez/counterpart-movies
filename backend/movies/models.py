from django.db import models
from django.db.models import (
    BooleanField,
    CharField,
    DecimalField,
    ForeignKey,
    IntegerField,
    JSONField,
    OneToOneField,
    TextField,
)
from pydantic import BaseModel, Field, validator


class Movie(models.Model):
    # Primary key for unique titles
    tconst: CharField = CharField(max_length=20, primary_key=True)

    # Index commonly searched/sorted fields
    title_type: CharField = CharField(max_length=50)
    title: CharField = CharField(
        max_length=200, db_index=True
    )  # Often filtered or sorted
    original_title: CharField = CharField(max_length=200, blank=True, null=True)
    is_adult: BooleanField = BooleanField(default=False)
    year: CharField = CharField(max_length=4, blank=True, null=True, db_index=True)
    end_year: CharField = CharField(max_length=4, blank=True, null=True)
    runtime: CharField = CharField(max_length=10, blank=True, null=True)
    genre: CharField = CharField(max_length=200, blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.title} ({self.year})"


class Name(models.Model):
    # Primary key for unique names
    nconst: CharField = CharField(max_length=20, primary_key=True)

    # Index 'name' if frequently searched
    name: CharField = CharField(max_length=200, db_index=True)
    birth_year: CharField = CharField(max_length=4, blank=True, null=True)
    death_year: CharField = CharField(max_length=4, blank=True, null=True)
    primary_professions: CharField = CharField(max_length=200, blank=True, null=True)
    known_for_titles: TextField = TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Principal(models.Model):
    tconst: ForeignKey = ForeignKey(Movie, on_delete=models.CASCADE)
    nconst: ForeignKey = ForeignKey(Name, on_delete=models.CASCADE)
    category: CharField = CharField(max_length=50)
    job: CharField = CharField(max_length=200, blank=True, null=True)
    characters: JSONField = JSONField(blank=True, null=True)

    def __str__(self):
        return f"{self.nconst.name} in {self.tconst.title} ({self.category})"


class Rating(models.Model):
    """
    Stores IMDb rating data for a movie.
    Linked to Movie by the same tconst.
    """

    tconst: OneToOneField = OneToOneField(
        Movie, on_delete=models.CASCADE, primary_key=True
    )
    # Index the rating if you frequently filter or sort by it
    average_rating: DecimalField = DecimalField(
        max_digits=3, decimal_places=1, db_index=True
    )
    num_votes: IntegerField = IntegerField()

    def __str__(self):
        return f"Rating for {self.tconst.title}: {self.average_rating} ({self.num_votes} votes)"


class MovieInput(BaseModel):
    tconst: str
    title_type: str
    title: str
    original_title: str | None = None
    is_adult: bool
    year: str | None = None
    end_year: str | None = None
    runtime: str | None = None
    genre: str | None = None


class PrincipalInput(BaseModel):
    tconst: str
    nconst: str
    category: str
    job: str | None = None
    characters: list[str] | None = None


class RatingInput(BaseModel):
    tconst: str
    average_rating: float
    num_votes: int


class SearchQueryParams(BaseModel):
    name: str | None = None
    title: str | None = None
    genre: str | None = None
    year: str | None = None
    category: str | None = None
    job: str | None = None
    characters: str | None = None
    sort: str | None = Field(default=None)
    order: str = Field(default="asc")
    exact: bool | str = Field(default=False)

    @validator("exact", pre=True)
    def parse_exact(cls, v: object) -> bool:
        """Convert strings like "true", "false" into booleans."""
        if not v:
            return False
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes")
        return False
