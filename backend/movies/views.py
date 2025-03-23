from typing import Any

from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import pagination, status
from rest_framework.decorators import api_view
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import Movie, MovieInput, Name, Principal, SearchQueryParams
from .serializers import MovieSerializer, NameSerializer, PrincipalSerializer
from .utils import (
    filter_movies,
    filter_names,
    filter_principals,
)


class StandardResultsSetPagination(pagination.PageNumberPagination):
    """
    Pagination settings for API responses.
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


@method_decorator(cache_page(60 * 15), name="dispatch")  # 15 min cache
class MovieViewSet(ModelViewSet):
    """
    API endpoint for managing movies.
    """

    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        We simply pass the request query params to our filter_movies utility.
        That function encapsulates all sorting/filtering logic.
        """
        base_qs = super().get_queryset()
        return filter_movies(self.request.query_params, base_qs=base_qs)


@method_decorator(cache_page(60 * 15), name="dispatch")  # 15 min cache
class PrincipalViewSet(ModelViewSet):
    """
    API endpoint for managing principals (actors, directors, etc.).
    """

    queryset = Principal.objects.all()
    serializer_class = PrincipalSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        base_qs = super().get_queryset()

        # If you need an extra filter, e.g. "tconst",
        # do that here before calling filter_principals.
        tconst = self.request.query_params.get("tconst")
        if tconst:
            base_qs = base_qs.filter(tconst__tconst=tconst)

        return filter_principals(self.request.query_params, base_qs=base_qs)


@method_decorator(cache_page(60 * 15), name="dispatch")  # 15 min cache
class NameViewSet(ModelViewSet):
    """
    API endpoint for managing names of people in the industry.
    """

    queryset = Name.objects.all()
    serializer_class = NameSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        base_qs = super().get_queryset()
        return filter_names(self.request.query_params, base_qs=base_qs)


class SearchAPIView(APIView):
    """
    API endpoint for searching movies, principals, and names
    with pagination, sorting, manual caching, and partial vs exact matching.
    """

    pagination_class = StandardResultsSetPagination

    def get(self, request: Request) -> Response:
        """Search movies, principals, and names with multiple filters."""
        raw_query_params: dict[str, str | list[str]] = dict(request.query_params)

        # If any value is a list, just take the first element
        single_params = {
            k: v[0] if isinstance(v, list) else v for k, v in raw_query_params.items()
        }

        try:
            params = SearchQueryParams(**single_params)
        except ValidationError as e:
            return Response(
                {"error": f"Invalid query parameters: {e}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build a unique cache key for these query parameters
        cache_key: str = f"search:{request.query_params.urlencode()}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # Ensure at least one param is present
        if not any(
            [
                params.name,
                params.title,
                params.genre,
                params.year,
                params.category,
                params.job,
                params.characters,
            ]
        ):
            return Response(
                {"error": "At least one search parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        paginator = self.pagination_class()
        serialized_data: list[dict[str, Any]] = []

        # 1) Filter movies if relevant query params are present
        has_movie_filters = any([params.title, params.genre, params.year])
        if has_movie_filters:
            movie_qs = filter_movies(single_params)
            movie_results = paginator.paginate_queryset(movie_qs, request)
            if movie_results:
                for m in movie_results:
                    serialized_data.append(
                        {"type": "movie", "data": MovieSerializer(m).data}
                    )

        # 2) Filter principals if relevant query params are present
        has_principal_filters = any([params.category, params.job, params.characters])
        if has_principal_filters:
            principal_qs = filter_principals(single_params)
            principal_results = paginator.paginate_queryset(principal_qs, request)
            if principal_results:
                for p in principal_results:
                    serialized_data.append(
                        {"type": "principal", "data": PrincipalSerializer(p).data}
                    )

        # 3) Filter names if relevant query params are present
        has_name_filters = params.name is not None
        if has_name_filters:
            name_qs = filter_names(single_params)
            name_results = paginator.paginate_queryset(name_qs, request)
            if name_results:
                for n in name_results:
                    serialized_data.append(
                        {"type": "name", "data": NameSerializer(n).data}
                    )

        if not serialized_data:
            return Response(
                {"message": "No results found."}, status=status.HTTP_404_NOT_FOUND
            )

        final_response = paginator.get_paginated_response(serialized_data)

        # Cache the final response (e.g. 5 minutes)
        cache.set(cache_key, final_response.data, timeout=60 * 5)
        return final_response


@api_view(["POST"])
def create_movie(request):
    """Example endpoint to create a new Movie using Pydantic validation."""
    try:
        data = request.data  # a dict from the request body
        pydantic_movie = MovieInput(**data)
    except ValidationError as e:
        return Response({"errors": e.errors()}, status=400)

    # If valid, create the Django object
    movie = Movie.objects.create(**pydantic_movie.dict())
    return Response({"message": "Movie created", "tconst": movie.tconst}, status=201)
