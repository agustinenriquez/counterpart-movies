from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import MovieViewSet, NameViewSet, PrincipalViewSet, SearchAPIView

router = DefaultRouter()
router.register(r"movies", MovieViewSet)
router.register(r"principals", PrincipalViewSet)
router.register(r"names", NameViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("search/", SearchAPIView.as_view(), name="search"),
]
