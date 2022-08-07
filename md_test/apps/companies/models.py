from django.db import models


class BaseModel(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)
        abstract = True


class Company(BaseModel):
    class Meta:
        ordering = ('name',)


class Office(BaseModel):
    company = models.ForeignKey('Company',
                                on_delete=models.CASCADE)
    country = models.CharField(max_length=256)
    city = models.CharField(max_length=256)
    region = models.CharField(max_length=256)


class Vehicle(models.Model):
    company = models.ForeignKey(Company,
                                on_delete=models.CASCADE)
    office = models.ForeignKey('Office',
                               on_delete=models.SET_DEFAULT,
                               default=None,
                               blank=True,
                               null=True,
                               related_name='vehicles')
    name = models.CharField(max_length=256)
    model = models.CharField(max_length=256)
    licence_plate = models.CharField(max_length=64)
    year_of_manufactured = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('pk', )
