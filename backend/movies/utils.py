from typing import Any

from django.db.models import Q, QuerySet


def parse_exact(exact_param: str) -> bool:
    """
    Convert a string like 'true', '1', 'yes' to a boolean True/False.
    Defaults to False for any other string (including empty).
    """
    return exact_param.lower() in ("true", "1", "yes")


def build_string_query(field: str, value: str, exact: bool) -> Q:
    """
    Return a Q object for either icontains or iexact,
    based on the `exact` parameter.
    """
    if exact:
        return Q(**{f"{field}__iexact": value})
    else:
        return Q(**{f"{field}__icontains": value})


def filter_movies(params: dict[str, Any], base_qs: QuerySet | None = None) -> QuerySet:
    """
    Apply various filters and sorting to a Movie queryset based
    on the query params.
    """
    from .models import Movie  # Local import to avoid circular imports

    if base_qs is None:
        base_qs = Movie.objects.all()

    queryset = base_qs
    exact = parse_exact(params.get("exact", "false"))

    # Filters
    min_rating = params.get("min_rating")
    title = params.get("title")
    genre = params.get("genre")
    year = params.get("year")

    # Sorting params
    sort_by = params.get("sort")
    order = params.get("order", "asc")
    order_prefix = "-" if order == "desc" else ""

    # 1) min_rating
    if min_rating:
        queryset = queryset.filter(rating__average_rating__gte=min_rating)

    # 2) Sorting logic
    if sort_by == "rating":
        sort_field = "rating__average_rating"
    elif sort_by == "year":
        sort_field = "year"
    else:
        # default to "title"
        sort_field = "title"
    queryset = queryset.order_by(f"{order_prefix}{sort_field}")

    # 3) Title filter (title or original_title)
    if title:
        if exact:
            queryset = queryset.filter(
                Q(title__iexact=title) | Q(original_title__iexact=title)
            )
        else:
            queryset = queryset.filter(
                Q(title__icontains=title) | Q(original_title__icontains=title)
            )

    # 4) Genre filter
    if genre:
        queryset = queryset.filter(build_string_query("genre", genre, exact))

    # 5) Year filter
    if year:
        queryset = queryset.filter(year=year)

    return queryset


def filter_principals(
    params: dict[str, Any], base_qs: QuerySet | None = None
) -> QuerySet:
    """
    Apply filters and sorting to a Principal queryset.
    """
    from .models import Principal

    if base_qs is None:
        base_qs = Principal.objects.all()

    queryset = base_qs
    exact = parse_exact(params.get("exact", "false"))

    category = params.get("category")
    job = params.get("job")
    characters = params.get("characters")

    sort = params.get("sort")
    order = params.get("order", "asc")
    order_prefix = "-" if order == "desc" else ""

    # Filters
    if category:
        queryset = queryset.filter(build_string_query("category", category, exact))
    if job:
        queryset = queryset.filter(build_string_query("job", job, exact))
    if characters:
        # For JSONField, this is a naive partial match approach
        queryset = queryset.filter(build_string_query("characters", characters, exact))

    # Sorting
    valid_principal_fields = ["id", "category", "job", "ordering"]
    if sort not in valid_principal_fields:
        sort = "id"
    queryset = queryset.order_by(f"{order_prefix}{sort}")

    return queryset


def filter_names(params: dict[str, Any], base_qs: QuerySet | None = None) -> QuerySet:
    """
    Apply filters and sorting to a Name queryset.
    """
    from .models import Name

    if base_qs is None:
        base_qs = Name.objects.all()

    queryset = base_qs
    exact = parse_exact(params.get("exact", "false"))
    name = params.get("name")

    sort = params.get("sort")
    order = params.get("order", "asc")
    order_prefix = "-" if order == "desc" else ""

    # Filter by name
    if name:
        queryset = queryset.filter(build_string_query("name", name, exact))

    # Sorting
    valid_name_fields = ["nconst", "name", "birth_year", "death_year"]
    if sort not in valid_name_fields:
        sort = "name"
    queryset = queryset.order_by(f"{order_prefix}{sort}")

    # Optional: Filter by comma-separated nconsts
    nconsts = params.get("nconsts")
    if nconsts:
        nconst_list = nconsts.split(",")
        queryset = queryset.filter(nconst__in=nconst_list)

    return queryset
