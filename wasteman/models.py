from django.contrib.gis.db import models as gis_models
from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import Point as GeoPoint
from django.db import models
from django.utils.translation import gettext_lazy as _
from geopy import Point
from geopy.geocoders import Nominatim

from accounts.models import CustomUser


class WasteType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Waste(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.ForeignKey(WasteType, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    location = gis_models.PointField(_('waste location'), geography=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    schedule = models.ForeignKey('Schedule', on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.location:
            # Set default location as user's location
            self.location = self.user.location
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}'s {self.type.name} - {self.quantity} kg"

    def waste_address(self):
        geolocator = Nominatim(user_agent="waste_management_app")
        location = geolocator.reverse((self.user.location.y, self.user.location.x))
        return location.address


class Meta:
    verbose_name_plural = "Waste"
    verbose_name = "Waste"


class WasteCollector(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    location = gis_models.PointField(_('collector location'), geography=True, null=True, blank=True, srid=4326, )

    class Meta:
        verbose_name_plural = "Waste Collectors"
        verbose_name = "Waste Collector"

    def __str__(self):
        return self.user.email

    def collector_address(self):
        geolocator = Nominatim(user_agent="waste_management_app")
        location = geolocator.reverse((self.location.y, self.location.x))
        return location.address


class IssueReport(models.Model):
    ISSUE_TYPE_CHOICES = (
        ('MissedPickup', 'Missed Pickup'),
        ('DamagedBin', 'Damaged Bin'),
        ('IllegalDumping', 'Illegal Dumping'),
        ('Other', 'Other'),
    )

    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('InProgress', 'In Progress'),
        ('Resolved', 'Resolved'),
        ('Closed', 'Closed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    issue_type = models.CharField(max_length=50, choices=ISSUE_TYPE_CHOICES, default='Other')
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.get_issue_type_display()} reported by {self.user.email} - Status: {self.status}"


class PickupZone(models.Model):
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, )
    longitude = models.DecimalField(max_digits=10, decimal_places=8)

    class Meta:
        verbose_name_plural = "Pickup Zones"

    @property
    def location(self):
        return Point(float(self.latitude), float(self.longitude))

    def __str__(self):
        return f"{self.name} - {self.zone_address()}"

    def zone_address(self):
        geolocator = Nominatim(user_agent="waste_management_app")
        location = geolocator.reverse((self.latitude, self.longitude))
        return location.address.split(",")[0]


class Schedule(models.Model):
    pickup_zone = models.ForeignKey(PickupZone, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    waste_collectors = models.ManyToManyField(WasteCollector)

    class Meta:
        verbose_name_plural = "Waste Schedules"

    def create_collection_status(self):
        try:
            # Automatically assign nearest collectors
            collector = assign_nearest_collector(self)
            if collector:
                # Create CollectionStatus instance for each collector
                CollectionStatus.objects.create(schedule=self, collector=collector)
        except Exception as e:
            print(f"Error: {e}")
            pass

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.create_collection_status()

    def __str__(self):
        return f"{self.pickup_zone.name} - {self.date} - {self.start_time} - {self.end_time}"


class CollectionStatus(models.Model):
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE)
    collector = models.ForeignKey(WasteCollector, on_delete=models.CASCADE)
    status_choices = [
        ('Pending', 'Pending'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')

    class Meta:
        verbose_name_plural = "Collection Status"

    def __str__(self):
        return f"{self.collector.user.email} - {self.schedule} - {self.status}"


class Resident(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    def user_location(self):
        return self.user.location

    class Meta:
        verbose_name_plural = "Residents"

    def __str__(self):
        return self.user.email

    @property
    def resident_address(self):
        loc = self.user_location()
        print(f"Location: {loc}")
        geolocator = Nominatim(user_agent="waste_management_app")
        location = geolocator.reverse((loc.y, loc.x))
        return location.address


def assign_nearest_collector(schedule):
    # Get the pickup zone location as a Point object
    pickup_zone_location = GeoPoint(
        schedule.pickup_zone.location.longitude,
        schedule.pickup_zone.location.latitude,
        srid=4326
    )

    # Query all waste collectors sorted by distance to the pickup zone
    nearest_collector = WasteCollector.objects.annotate(
        distance=Distance('location', pickup_zone_location)
    ).order_by('distance').first()  # Get the closest collector

    if nearest_collector:
        schedule.waste_collectors.add(nearest_collector)
        return nearest_collector

    else:
        raise ValueError("No waste collectors available")
