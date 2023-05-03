from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from django_filters import rest_framework as filters
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from django.db.models.functions import Cast
from .serializers import CarDataSerializer
from django.db.models import IntegerField
from rest_framework.views import APIView
from rest_framework import generics
from django.db.models import Q
from .models import CarData


# Create your views here.

# Adding Pagination for car listings
class CustomPagination(PageNumberPagination):
    page_size = 15
    max_page_size = 50
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        car_data = []
        for item in data:
            # body_typ, trans, engine = "", "", ""
            mileage, trans, fuel = "", "", ""
            for itm in item.get("car_data").get("overview") if item.get("car_data").get("overview") else []:
                if itm.get("label") == "Transmissietype":
                    trans = itm.get("value")
                if itm.get("label") == "Brandstof":
                    fuel = itm.get("value")
            for itm in item.get("car_data").get("specs") if item.get("car_data").get("specs") else []:
                for ittm in itm.get("specs"):
                    if ittm.get("name") == "Transmissietype":
                        trans = ittm.get("value")
                    if ittm.get("name") == "Brandstof":
                        fuel = ittm.get("value")
                    if ittm.get("name") == "Kilometerstand":
                        mileage = ittm.get("value")
            car = {
                "fuel": fuel,
                "mileage": mileage,
                "trans": trans,
                "title": "",
                "subtitle": "",
                "price": "",
                "year": "",
                "images": "",
                "location": item.get("car_data").get("seller").get("city")
            }
            for k, v in item.get("car_data").get("general").items():
                if k == "images":
                    if len(v) != 0:
                        v = v[0]
                if k in list(car.keys()):
                    car[k] = v
            car_data.append({
                "id": item.get("id"),
                "car_id": item.get("car_id"),
                "car": car
            })
        carData = {
            'Data': car_data,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count
        }
        return Response(carData)

# Adding Filters to get specific cars from database
class CarFilters(filters.FilterSet):
    make = filters.CharFilter(method='filter_make')
    model = filters.CharFilter(method='filter_model')
    body_typ = filters.CharFilter(method='filter_body_typ')
    year = filters.CharFilter(method='filter_year')
    fuel = filters.CharFilter(method='filter_fuel_typ')
    trans = filters.CharFilter(method='filter_trans')
    mileage = filters.CharFilter(method='filter_mileage')
    title = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = CarData
        fields = ['make', 'model', 'body_typ', 'year', 'title', 'fuel', 'trans', 'mileage']

    def filter_make(self, queryset, name, value):
        makes = value.split(',')
        q_objects = Q()
        for make in makes:
            q_objects |= Q(make=make.strip())
        return queryset.filter(q_objects)

    def filter_model(self, queryset, name, value):
        models = value.split(',')
        all_makes = self.data.get("make")
        if all_makes:
            for make in all_makes.split(","):
                new_models = get_models_list(make)
                chk = False
                for m in value.split(','):
                    if m in new_models:
                        chk = True
                if not chk:
                    for m in new_models:
                        models.append(m)
        q_objects = Q()
        for model in models:
            q_objects |= Q(model=model.strip())
        return queryset.filter(q_objects)
    

    def filter_body_typ(self, queryset, name, value):
        body_types = value.split(',')
        q_objects = Q()
        for body_type in body_types:
            q_objects |= Q(body_typ=body_type.strip())
        return queryset.filter(q_objects)
    
    def filter_fuel_typ(self, queryset, name, value):
        fuel_types = value.split(',')
        q_objects = Q()
        for fuel_type in fuel_types:
            q_objects |= Q(fuel=fuel_type.strip())
        return queryset.filter(q_objects)
    
    def filter_trans(self, queryset, name, value):
        trans = value.split(',')
        q_objects = Q()
        for tran in trans:
            q_objects |= Q(trans=tran.strip())
        return queryset.filter(q_objects)
    
    def filter_year(self, queryset, name, value):
        years = value.strip(",").split(",")
        if value.strip() != ',':
            if len(years) == 2:
                queryset = queryset.filter(year__range=(years[0].strip(), years[1].strip()))
            elif len(years) == 1:
                queryset = queryset.filter(year__icontains=years[0])
        return queryset
    
    def filter_mileage(self, queryset, name, value):
        mileage = value.split(",")
        if len(mileage) == 2:
            queryset = queryset.filter(mileage__isnull=False).annotate(mileage_int=Cast('mileage', IntegerField())).filter(mileage_int__gte=int(mileage[0].strip()), mileage_int__lte=int(mileage[1].strip()))
            # queryset = queryset.filter(mileage__range=(mileage[0].strip(), mileage[1].strip()))
        elif len(mileage) == 1:
            queryset = queryset.filter(mileage__isnull=False).annotate(mileage_int=Cast('mileage', IntegerField()))
            queryset = queryset.filter(mileage=mileage[0])
        return queryset
    
# Get List of models from CarData Model
def get_models_list(make):
    queryset = CarData.objects.filter(year__gte=2013, make=make)
    models = []
    for item in queryset:
        if item.model not in models:
            models.append(item.model)
    return models

# Get Listing of cars with few details
class CarListingView(generics.ListAPIView):
    queryset = CarData.objects.filter(year__gte=2013).order_by("-created")
    serializer_class = CarDataSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = CarFilters
    pagination_class = CustomPagination

    # cars = CarData.objects.all()
    # for i, car in enumerate(cars):
    #     car.update_from_json()
    #     print(i)
    

# Getting All Available Makes and Models
class CarMakeModel(generics.ListAPIView):
    queryset = CarData.objects.filter(year__gte=2013)
    serializer_class = CarDataSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        make_model_data = {}
        for item in serializer.data:
            make = item.get("make")
            model = item.get("model")
            body_typ = item.get("body_typ")
            if make not in list(make_model_data.keys()):
                make_model_data[make] = {
                    "models": [],
                    "body_types": []
                }
            if model not in make_model_data.get(make).get("models"):
                make_model_data.get(make).get("models").append(model)
            if body_typ not in make_model_data.get(make).get("body_types"):
                make_model_data.get(make).get("body_types").append(body_typ)
        return Response(make_model_data)
    
# Getting All Transmissions and Body Types
class CarTransBody(generics.ListAPIView):
    queryset = CarData.objects.filter(year__gte=2013)
    serializer_class = CarDataSerializer
    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        cmp = {
            "transmission": [],
            "body_types": [],
            "fuel_types": []
        }
        for item in serializer.data:
            body_typ = item.get("body_typ")
            trans = item.get("trans")
            fuel = ""
            for itm in item.get("car_data").get("overview") if item.get("car_data").get("overview") else []:
                if itm.get("label") == "Brandstof":
                    fuel = itm.get("value")
            for itm in item.get("car_data").get("specs") if item.get("car_data").get("specs") else []:
                for ittm in itm.get("specs"):
                    if ittm.get("name") == "Brandstof":
                        fuel = ittm.get("value")
            if trans not in cmp.get("transmission"):
                if trans != "-":
                    cmp.get("transmission").append(trans)
            if body_typ not in cmp.get("body_types"):
                if body_typ != "":
                    cmp.get("body_types").append(body_typ)
            if fuel not in cmp.get("fuel_types"):
                cmp.get("fuel_types").append(fuel)
        return Response(cmp)

# Get Latest Added Cars
class CarLatestOffersView(generics.ListAPIView):
    queryset = CarData.objects.filter(year__gte=2013).order_by("-created")[:10]
    serializer_class = CarDataSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        car_data = []
        for item in serializer.data:
            # body_typ, trans, engine = "", "", ""
            mileage, trans, fuel = "", "", ""
            for itm in item.get("car_data").get("overview") if item.get("car_data").get("overview") else []:
                if itm.get("label") == "Transmissietype":
                    trans = itm.get("value")
                if itm.get("label") == "Brandstof":
                    fuel = itm.get("value")
            for itm in item.get("car_data").get("specs") if item.get("car_data").get("specs") else []:
                for ittm in itm.get("specs"):
                    # if ittm.get("name") == "Transmissietype":
                    #     trans = ittm.get("value")
                    if ittm.get("name") == "Brandstof":
                        fuel = ittm.get("value")
                    if ittm.get("name") == "Kilometerstand":
                        mileage = ittm.get("value")
            car = {
                "fuel": fuel,
                "mileage": mileage,
                "trans": trans,
                "title": "",
                "subtitle": "",
                "price": "",
                "year": "",
                "images": "",
                "location": item.get("car_data").get("seller").get("city")
            }
            for k, v in item.get("car_data").get("general").items():
                if k == "images":
                    if len(v) != 0:
                        v = v[0]
                if k in list(car.keys()):
                    car[k] = v
            car_data.append({
                "id": item.get("id"),
                "car_id": item.get("car_id"),
                "car": car
            })
        carData = {
            'Data': car_data
        }
        return Response(carData)

# Get Ids Of All Cars
class GetCarIds(generics.ListAPIView):
    queryset = CarData.objects.all()
    serializer_class = CarDataSerializer

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        car_ids = [int(item.get("car_id")) for item in serializer.data]
        return Response(car_ids)


# Add New Car To DataBase
class AddCarDataView(APIView):
    parser_classes = [JSONParser]
    renderer_classes = [JSONRenderer]

    def post(self, request):
        if request.content_type != 'application/json':
            return Response({"Error": True, "Msg": 'Invalid Data Type'}, status=400)
        serializer = CarDataSerializer(data=request.data)
        if serializer.is_valid():
            if CarData.objects.filter(car_id=request.data.get("car_id")).exists():
                return Response({"Error": True, "Msg": 'Already Exists'}, status=403)
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


# Get Full Detail of Single Car
class CarDetailView(APIView):
    def get(self, request, pk):
        try:
            car = CarData.objects.get(pk=pk)
        except CarData.DoesNotExist:
            return Response(status=404)
        serializer = CarDataSerializer(car)
        return Response(serializer.data)