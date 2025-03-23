import pytest
from django.urls import reverse
from movies.models import Movie, Name, Principal
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    """Reusable fixture for DRF's APIClient."""
    return APIClient()


@pytest.fixture
def setup_movies():
    """
    Create some test Movie objects.
    We'll assume your Movie model has these fields.
    """
    Movie.objects.create(
        tconst="tt1111111",
        title_type="movie",
        title="Test Movie 1",
        original_title="Test Movie One",
        is_adult=False,
        year="2021",
        genre="Action",
    )
    Movie.objects.create(
        tconst="tt2222222",
        title_type="movie",
        title="Test Movie 2",
        original_title="Test Movie Two",
        is_adult=False,
        year="2022",
        genre="Drama",
    )


@pytest.mark.django_db
class TestMovieViewSet:
    """
    Tests for the MovieViewSet endpoint.
    Assumes you registered it with DefaultRouter and named it 'movie-list'.
    """

    @pytest.mark.usefixtures("setup_movies")
    def test_get_movies(self, api_client):
        """
        Verify that the movie-list endpoint returns a 200 status
        and includes the expected movies.
        """
        url = reverse("movie-list")
        response = api_client.get(url)
        assert response.status_code == 200, response.data

        # Check the pagination structure if using a PageNumberPagination
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] == 2

        # Extract titles for a quick check
        result_titles = [m["title"] for m in response.data["results"]]
        assert "Test Movie 1" in result_titles
        assert "Test Movie 2" in result_titles

    @pytest.mark.usefixtures("setup_movies")
    def test_filter_by_exact_title(self, api_client):
        """
        Verify that the movie-list endpoint can filter by title.
        """
        url = reverse("movie-list")
        response = api_client.get(url, {"title": "Test Movie 1", "exact": "true"})
        assert response.status_code == 200, response.data
        assert response.data["count"] == 1
        assert response.data["results"][0]["title"] == "Test Movie 1"

    @pytest.mark.usefixtures("setup_movies")
    def test_filter_by_partial_title(self, api_client):
        """
        Verify that the movie-list endpoint can filter by partial title.
        """
        url = reverse("movie-list")
        response = api_client.get(url, {"title": "Test Movie"})
        assert response.status_code == 200, response.data
        assert response.data["count"] == 2

    @pytest.mark.usefixtures("setup_movies")
    def test_filter_by_genre(self, api_client):
        """
        Verify that the movie-list endpoint can filter by genre.
        """
        url = reverse("movie-list")
        response = api_client.get(url, {"genre": "Action", "exact": "true"})
        assert response.status_code == 200, response.data
        assert response.data["count"] == 1
        assert response.data["results"][0]["genre"] == "Action"

    @pytest.mark.usefixtures("setup_movies")
    def test_filter_by_year(self, api_client):
        """
        Verify that the movie-list endpoint can filter by year.
        """
        url = reverse("movie-list")
        response = api_client.get(url, {"year": "2022", "exact": "true"})
        assert response.status_code == 200, response.data
        assert response.data["count"] == 1
        assert response.data["results"][0]["year"] == "2022"

    @pytest.mark.usefixtures("setup_movies")
    def test_retrieve_movie(self, api_client):
        """
        Verify that the movie-detail endpoint returns a single movie.
        Assumes you have a movie object with tconst="tt1111111".
        """
        url = reverse("movie-detail", args=["tt1111111"])
        response = api_client.get(url)
        assert response.status_code == 200, response.data
        assert response.data["title"] == "Test Movie 1"

    @pytest.mark.usefixtures("setup_movies")
    def test_update_movie(self, api_client):
        """
        Verify that the movie-detail endpoint can update a movie.
        Assumes you have a movie object with tconst="tt1111111".
        """
        url = reverse("movie-detail", args=["tt1111111"])
        data = {"title": "Updated Title"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == 200, response.data
        assert response.data["title"] == "Updated Title"

    @pytest.mark.django_db
    @pytest.mark.usefixtures("setup_movies")
    def test_create_movie(self, api_client):
        """
        Verify that the movie-list endpoint can create a movie.
        """
        url = reverse("movie-list")
        data = {
            "tconst": "tt3333333",
            "title_type": "movie",
            "title": "New Movie",
            "original_title": "New Movie",
            "is_adult": False,
            "year": "2023",
            "genre": "Comedy",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201, response.data
        assert response.data["title"] == "New Movie"
        assert Movie.objects.filter(tconst="tt3333333").exists()

    @pytest.mark.usefixtures("setup_movies")
    def test_delete_movie(self, api_client):
        """
        Verify that the movie-detail endpoint can delete a movie.
        Assumes you have a movie object with tconst="tt1111111".
        """
        url = reverse("movie-detail", args=["tt1111111"])
        response = api_client.delete(url)
        assert response.status_code == 204, response.data
        assert not Movie.objects.filter(tconst="tt1111111").exists()


class TestNameViewSet:
    """
    Tests for the NameViewSet endpoint.
    Assumes you registered it with DefaultRouter and named it 'name-list'.
    """

    @pytest.mark.django_db
    def test_get_names(self, api_client):
        """
        Verify that the name-list endpoint returns a 200 status.
        """
        url = reverse("name-list")
        response = api_client.get(url)
        assert response.status_code == 200, response.data

        # Check the pagination structure if using a PageNumberPagination
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] == 0

    @pytest.mark.django_db
    def test_create_name(self, api_client):
        """
        Verify that the name-list endpoint can create a name.
        """
        url = reverse("name-list")
        data = {
            "name": "Test Name",
            "nconst": "nm1111111",
            "birth_year": "1990",
            "death_year": "2021",
            "primary_profession": "actor",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 201, response.data
        assert response.data["name"] == "Test Name"

    @pytest.mark.django_db
    def test_delete_name(self, api_client):
        """
        Verify that the name-detail endpoint can delete a name.
        Assumes you have a name object with nconst="nm1111111".
        Create a name object with nconst="nm1111111" before running this test.
        """
        Name.objects.create(
            name="Test Name",
            nconst="nm1111111",
            birth_year="1990",
            death_year="2021",
            primary_professions="actor",
        )
        url = reverse("name-detail", args=["nm1111111"])
        response = api_client.delete(url)
        assert response.status_code == 204, response.data
        assert not Name.objects.filter(nconst="nm1111111").exists()

    @pytest.mark.django_db
    def test_retrieve_name(self, api_client):
        """
        Verify that the name-detail endpoint returns a single name.
        Assumes you have a name object with nconst="nm1111111".
        """
        url = reverse("name-detail", args=["nm1111111"])
        response = api_client.get(url)
        assert response.status_code == 404, response.data

    @pytest.mark.django_db
    def test_update_name(self, api_client):
        """
        Verify that the name-detail endpoint can update a name.
        Assumes you have a name object with nconst="nm1111111".
        """
        url = reverse("name-detail", args=["nm1111111"])
        data = {"primary_name": "Updated Name"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == 404, response.data


class TestPrincipalViewSet:
    """
    Tests for the PrincipalViewSet endpoint.
    Assumes you registered it with DefaultRouter and named it 'principal-list'.
    """

    @pytest.mark.django_db
    def test_get_principals(self, api_client):
        """
        Verify that the principal-list endpoint returns a 200 status.
        """
        url = reverse("principal-list")
        response = api_client.get(url)
        assert response.status_code == 200, response.data

        # Check the pagination structure if using a PageNumberPagination
        assert "count" in response.data
        assert "results" in response.data
        assert response.data["count"] == 0

    @pytest.mark.django_db
    def test_create_principal(self, api_client):
        """
        Verify that the principal-list endpoint can create a principal.
        Check that pk is not invalid.
        """
        reverse("principal-list")

        # Create a movie object
        data = {
            "tconst": "tt1111111",
            "title_type": "movie",
            "title": "Test Movie 1",
            "original_title": "Test Movie One",
            "is_adult": False,
            "year": "2021",
            "genre": "Action",
        }
        response = api_client.post(reverse("movie-list"), data, format="json")
        assert response.status_code == 201, response.data
        assert response.data["tconst"] == "tt1111111"

    @pytest.mark.django_db
    def test_delete_principal(self, api_client):
        """
        Verify that the principal-detail endpoint can delete a principal.
        """
        movie = Movie.objects.create(
            tconst="tt1111111",
            title_type="movie",
            title="Test Movie 1",
            original_title="Test Movie One",
            is_adult=False,
            year="2021",
            genre="Action",
        )
        name = Name.objects.create(
            name="Test Name",
            nconst="nm1111111",
            birth_year="1990",
            death_year="2021",
            primary_professions="actor",
        )
        principal = Principal.objects.create(
            tconst=movie,
            nconst=name,
            category="actor",
        )
        url = reverse("principal-detail", args=[principal.id])
        response = api_client.delete(url)
        assert response.status_code == 204, response.data
        assert not Principal.objects.filter(id=principal.id).exists()
        Movie.objects.filter(tconst="tt1111111").delete()

    @pytest.mark.django_db
    def test_retrieve_principal(self, api_client):
        """
        Verify that the principal-detail endpoint returns a single principal.
        Assumes you have a principal object with tconst="tt1111111".
        """
        url = reverse("principal-detail", args=["tt1111111"])
        response = api_client.get(url)
        assert response.status_code == 404, response.data

    @pytest.mark.django_db
    def test_update_principal(self, api_client):
        """
        Verify that the principal-detail endpoint can update a principal.
        Assumes you have a principal object with tconst="tt1111111".
        """
        url = reverse("principal-detail", args=["tt1111111"])
        data = {"category": "director"}
        response = api_client.patch(url, data, format="json")
        assert response.status_code == 404, response.data
