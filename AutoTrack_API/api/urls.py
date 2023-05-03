from .views import AddCarDataView, CarDetailView, CarLatestOffersView, CarListingView, GetCarIds, CarMakeModel, CarTransBody
from django.urls import path


urlpatterns = [
    path("listings/", CarListingView.as_view(), name="car_listings"),
    path("detail/<int:pk>", CarDetailView.as_view(), name="car_detail"),
    path("add_car", AddCarDataView.as_view(), name="add_car"),
    path("new-offers/", CarLatestOffersView.as_view(), name="offers"),
    path("get_car_ids/", GetCarIds.as_view(), name="car_ids"),
    path("get_make_models/", CarMakeModel.as_view(), name="make_model"),
    path("car-types/", CarTransBody.as_view(), name="car_types")
]