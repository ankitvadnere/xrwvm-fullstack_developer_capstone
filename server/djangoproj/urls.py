
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

from djangoapp import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Required API endpoints
    path("fetchDealers", views.get_dealerships, name="fetch_dealers"),
    path("fetchDealers/<str:state>", views.get_dealers_by_state, name="fetch_dealers_by_state"),
    path("fetchDealer/<int:dealer_id>", views.get_dealer_details, name="fetch_dealer"),
    path("fetchReviews/dealer/<int:dealer_id>", views.get_dealer_reviews, name="fetch_reviews"),

    # Existing application routes
    path("djangoapp/", include("djangoapp.urls")),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dealers/", views.dealers_home, name="dealers_home"),
    path("", views.home, name="home"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
