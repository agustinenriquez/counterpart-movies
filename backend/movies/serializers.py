from rest_framework import serializers

from .models import Movie, Name, Principal, Rating


class PrincipalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Principal
        fields = "__all__"


class NameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Name
        fields = "__all__"


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["average_rating", "num_votes"]


class MovieSerializer(serializers.ModelSerializer):
    rating = RatingSerializer(read_only=True)

    class Meta:
        model = Movie
        fields = [
            "tconst",
            "title_type",
            "title",
            "original_title",
            "is_adult",
            "year",
            "end_year",
            "runtime",
            "genre",
            "rating",
        ]
