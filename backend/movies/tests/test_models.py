import pytest
from django.db import IntegrityError
from movies.models import Movie, Name, Principal


@pytest.mark.django_db
class TestModels:
    """Tests for the Movie, Name, and Principal models."""

    def test_movie_str(self):
        """Ensure the Movie __str__ returns 'title (year)'."""
        movie = Movie.objects.create(
            tconst="tt9999999",
            title_type="movie",
            title="Test Title",
            original_title="Test Original Title",
            is_adult=False,
            year="2025",
        )
        assert str(movie) == "Test Title (2025)"

    def test_principal_str(self):
        """Ensure the Principal __str__ returns 'Person in Movie (category)'."""
        movie = Movie.objects.create(
            tconst="tt9999998",
            title_type="movie",
            title="A Test Movie",
            original_title="A Test Movie Original",
            is_adult=False,
            year="2025",
        )
        person = Name.objects.create(
            nconst="nm9999999", name="Test Person", birth_year="1980"
        )
        principal = Principal.objects.create(
            tconst=movie, nconst=person, category="actor"
        )
        assert str(principal) == "Test Person in A Test Movie (actor)"

    def test_name_str(self):
        """Ensure the Name __str__ returns just the person's name."""
        person = Name.objects.create(
            nconst="nm1111111", name="Jane Doe", birth_year="1970"
        )
        assert str(person) == "Jane Doe"

    @pytest.mark.django_db
    def test_movie_null_fields(self):
        """Ensure nullable fields can be saved & read properly."""
        movie = Movie.objects.create(
            tconst="tt9999911",
            title_type="movie",
            title="Null Fields Movie",
            is_adult=False,
            # year omitted -> null
            # original_title omitted -> blank or null
        )
        assert movie.year is None
        assert movie.original_title is None

    @pytest.mark.django_db
    def test_unique_tconst(self):
        Movie.objects.create(tconst="tt1234567", title="Unique Movie")
        with pytest.raises(IntegrityError):
            Movie.objects.create(tconst="tt1234567", title="Duplicate Movie")
