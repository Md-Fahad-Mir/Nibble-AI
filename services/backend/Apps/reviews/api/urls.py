from django.urls import path

from Apps.reviews.api import views

app_name = "reviews"

_rc = "brands/<uuid:brand_id>/review-campaigns"

urlpatterns = [
    # Brand: review campaigns
    path(f"{_rc}/", views.ReviewCampaignListCreateView.as_view(), name="campaign-list"),
    path(f"{_rc}/<uuid:campaign_id>/", views.ReviewCampaignDetailView.as_view(), name="campaign-detail"),
    path(f"{_rc}/<uuid:campaign_id>/products/", views.ReviewCampaignProductsView.as_view(), name="campaign-products"),
    path(f"{_rc}/<uuid:campaign_id>/prompts/", views.ReviewCampaignPromptsView.as_view(), name="campaign-prompts"),
    path(f"{_rc}/<uuid:campaign_id>/generate-prompts/", views.ReviewCampaignGeneratePromptsView.as_view(), name="campaign-generate-prompts"),
    path(f"{_rc}/<uuid:campaign_id>/activate/", views.ReviewCampaignActivateView.as_view(), name="campaign-activate"),
    path(f"{_rc}/<uuid:campaign_id>/pause/", views.ReviewCampaignPauseView.as_view(), name="campaign-pause"),
    path(f"{_rc}/<uuid:campaign_id>/preview/", views.ReviewCampaignPreviewView.as_view(), name="campaign-preview"),
    # Brand: moderation
    path("brands/<uuid:brand_id>/reviews/", views.BrandReviewListView.as_view(), name="brand-review-list"),
    path("brands/<uuid:brand_id>/reviews/<uuid:review_id>/remove/", views.BrandReviewRemoveView.as_view(), name="brand-review-remove"),
    # Consumer
    path("reviews/opportunities/", views.ReviewOpportunitiesView.as_view(), name="opportunities"),
    path("reviews/sessions/<uuid:session_id>/", views.ReviewSessionDetailView.as_view(), name="session-detail"),
    path("reviews/sessions/<uuid:session_id>/answer/", views.ReviewSessionAnswerView.as_view(), name="session-answer"),
    path("reviews/sessions/<uuid:session_id>/submit/", views.ReviewSessionSubmitView.as_view(), name="session-submit"),
    path("reviews/", views.MyReviewsView.as_view(), name="my-reviews"),
]
