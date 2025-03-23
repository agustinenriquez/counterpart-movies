import pytest
from movies.models import Movie, Name, Principal
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Reusable fixture for DRF's APIClient."""
    return APIClient()


@pytest.mark.django_db
class TestSearchAPI:
    """Comprehensive tests for the /api/search/ endpoint."""

    def test_search_api_returns_no_results(self, api_client):
        """If there's no matching record, the search endpoint should return 404."""
        url = "/api/search/?title=NonExistent"
        response = api_client.get(url)
        assert response.status_code == 404
        assert response.data["message"] == "No results found."

    def test_search_api_finds_movies(self, api_client):
        """Search endpoint should find movies by partial title."""
        # Create a test movie
        Movie.objects.create(
            tconst="tt5555555",
            title_type="movie",
            title="Moana Reloaded",
            original_title="Moana Reloaded",
            is_adult=False,
            year="2030",
        )
        url = "/api/search/?title=Moana+Relo"
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1  # 1 result
        results = response.data["results"]
        assert results[0]["type"] == "movie"
        assert results[0]["data"]["title"] == "Moana Reloaded"

    def test_search_api_finds_names(self, api_client):
        """Search endpoint should find names by partial match."""
        Name.objects.create(
            nconst="nm0000002", name="Rowan Atkinson", birth_year="1955"
        )
        url = "/api/search/?name=Rowan"
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        results = response.data["results"]
        assert results[0]["type"] == "name"
        assert results[0]["data"]["name"] == "Rowan Atkinson"

    def test_search_api_finds_principals(self, api_client):
        """Search endpoint should find principals by category."""
        movie = Movie.objects.create(
            tconst="tt8888888",
            title_type="movie",
            title="Test Principal Movie",
            original_title="Test Principal Movie",
            is_adult=False,
            year="2024",
        )
        person = Name.objects.create(
            nconst="nm8888888", name="Test Principal Person", birth_year="1985"
        )
        Principal.objects.create(tconst=movie, nconst=person, category="director")

        url = "/api/search/?category=director"
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 1
        result = response.data["results"][0]
        assert result["type"] == "principal"
        assert result["data"]["category"] == "director"
        assert result["data"]["tconst"] == "tt8888888"
        assert result["data"]["nconst"] == "nm8888888"

    def test_search_api_sort_pagination(self, api_client):
        """Search endpoint should respect 'sort' and 'order' params."""
        Movie.objects.create(tconst="tt0000001", title_type="movie", title="A Movie")
        Movie.objects.create(tconst="tt0000002", title_type="movie", title="B Movie")
        Movie.objects.create(tconst="tt0000003", title_type="movie", title="C Movie")

        # Test ascending sort by tconst, page_size=2
        url = "/api/search/?title=Movie&sort=tconst&order=asc&page_size=2"
        response = api_client.get(url)

        assert response.status_code == 200
        assert response.data["count"] == 3
        assert len(response.data["results"]) == 2  # Only 2 results on this page
        # First two should be tt0000001, tt0000002
        assert response.data["results"][0]["data"]["tconst"] == "tt0000001"
        assert response.data["results"][1]["data"]["tconst"] == "tt0000002"

        # Next page
        next_page = response.data["next"]
        response_page_2 = api_client.get(next_page)
        assert response_page_2.status_code == 200
        # Should have 1 result
        assert len(response_page_2.data["results"]) == 1
        assert response_page_2.data["results"][0]["data"]["tconst"] == "tt0000003"
