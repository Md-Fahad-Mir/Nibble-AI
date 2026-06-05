from django.urls import path

from Apps.offers.api import views

app_name = "offers"

urlpatterns = [
    path("offers/", views.OfferFeedView.as_view(), name="feed"),
    path(
        "offers/by-url/<str:token>/",
        views.OfferByURLView.as_view(),
        name="by-url",
    ),
    path(
        "offers/by-qr/<str:token>/",
        views.OfferByQRView.as_view(),
        name="by-qr",
    ),
    path(
        "offers/<uuid:campaign_id>/",
        views.OfferDetailView.as_view(),
        name="detail",
    ),
    path("bookmarks/", views.BookmarkListCreateView.as_view(), name="bookmark-list"),
    path(
        "bookmarks/<uuid:bookmark_id>/",
        views.BookmarkDeleteView.as_view(),
        name="bookmark-delete",
    ),
]
