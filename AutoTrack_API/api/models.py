from django.db import models


# Create your models here.
class CarData(models.Model):
    car_id = models.CharField(max_length=200)
    title = models.CharField(max_length=200, blank=True, null=True)
    make = models.CharField(max_length=200, blank=True, null=True)
    model = models.CharField(max_length=200, blank=True, null=True)
    year = models.CharField(max_length=200, blank=True, null=True)
    body_typ = models.CharField(max_length=200, blank=True, null=True)
    trans = models.CharField(max_length=200, blank=True, null=True)
    mileage = models.CharField(max_length=200, blank=True, null=True)
    fuel = models.CharField(max_length=200, blank=True, null=True)
    car_data = models.JSONField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.car_data.get("general").get("title")
    
    def save(self, *args, **kwargs) -> None:
        self.title = self.car_data.get("general").get("title")
        make, model, year, body_typ, trans, mileage, fuel = "", "", "", "", "", "", ""
        for itm in self.car_data.get("overview") if self.car_data.get("overview") else []:
            if itm.get("label") == "Brandstof":
                fuel = itm.get("value")
        for itm in self.car_data.get("specs") if self.car_data.get("specs") else []:
            for ittm in itm.get("specs"):
                if ittm.get("name") == "Merk":
                    make = ittm.get("value")
                if ittm.get("name") == "Model":
                    model = ittm.get("value")
                if ittm.get("name") == "Bouwjaar":
                    year = ittm.get("value")
                if ittm.get("name") == "Carrosserievorm":
                    body_typ = ittm.get("value")
                if ittm.get("name") == "Transmissietype":
                    trans = ittm.get("value")
                if ittm.get("name") == "Kilometerstand":
                    mileage = ittm.get("value")
                if ittm.get("name") == "Brandstof":
                    fuel = ittm.get("value")
        self.make = make
        self.model = model
        self.year = year
        self.body_typ = body_typ
        self.trans = trans
        self.mileage = mileage
        self.fuel = fuel
        super().save(*args, **kwargs)

    def update_from_json(self):
        self.title = self.car_data.get("general").get("title")
        make, model, year, body_typ, trans, mileage, fuel = "", "", "", "", "", "", ""
        for itm in self.car_data.get("overview") if self.car_data.get("overview") else []:
            if itm.get("label") == "Brandstof":
                fuel = itm.get("value")
        for itm in self.car_data.get("specs") if self.car_data.get("specs") else []:
            for ittm in itm.get("specs"):
                if ittm.get("name") == "Merk":
                    make = ittm.get("value")
                if ittm.get("name") == "Model":
                    model = ittm.get("value")
                if ittm.get("name") == "Bouwjaar":
                    year = ittm.get("value")
                if ittm.get("name") == "Carrosserievorm":
                    body_typ = ittm.get("value")
                if ittm.get("name") == "Transmissietype":
                    trans = ittm.get("value")
                if ittm.get("name") == "Kilometerstand":
                    mileage = ittm.get("value")
                if ittm.get("name") == "Brandstof":
                    fuel = ittm.get("value")
        self.make = make
        self.model = model
        self.year = year
        self.body_typ = body_typ
        self.trans = trans
        self.mileage = mileage
        self.fuel = fuel
        self.save()