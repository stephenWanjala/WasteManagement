from datetime import date

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user manager to handle residents and waste collectors.
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom user model to handle residents and waste collectors.
    """
    username = None
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    is_resident = models.BooleanField(_('resident status'), default=False)
    is_collector = models.BooleanField(_('collector status'), default=False)
    location = gis_models.PointField(_('user location'), geography=True, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class WasteType(models.Model):
    """
    Model for waste types.
    """
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name


class Waste(models.Model):
    """
    Model for waste.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    type = models.ForeignKey(WasteType, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    location = gis_models.PointField(_('waste location'), geography=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email}'s {self.type.name} - {self.quantity} kg"


class WasteCollector(models.Model):
    """
    Model for waste collectors.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    location = gis_models.PointField(_('collector location'), geography=True, null=True, blank=True)

    def assign_closest_pickup_zones(self):
        """
        Assigns pickup zones to the waste collector based on their location.
        """
        # Get the waste collector's location
        collector_location = self.location

        # Get all pickup zones
        pickup_zones = PickupZone.objects.all()

        # Calculate distances between the collector's location and pickup zones
        closest_pickup_zones = sorted(
            pickup_zones,
            key=lambda zone: collector_location.distance(zone.location)
        )

        # Assign the closest pickup zones to the collector
        for zone in closest_pickup_zones:
            # Get or create a schedule for the pickup zone and the current date
            schedule, created = Schedule.objects.get_or_create(pickup_zone=zone, date=date.today())

            # Assign the collector to the schedule if not already assigned
            if not schedule.waste_collectors.filter(pk=self.pk).exists():
                schedule.waste_collectors.add(self)

    class Meta:
        verbose_name_plural = "Waste Collectors"
        verbose_name = "Waste Collector"

    def __str__(self):
        return self.user.email


class IssueReport(models.Model):
    """
    Model for issue reports.
    """
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
    """
    Model for pickup zones.
    """
    name = models.CharField(max_length=100)
    location = gis_models.PointField(geography=True)

    class Meta:
        verbose_name_plural = "Pickup Zones"

    def __str__(self):
        return f"{self.name} - {self.location.verbose_name} - {self.location.x}, {self.location.y}"


class Schedule(models.Model):
    """
    Model for pickup schedules.
    """
    pickup_zone = models.ForeignKey(PickupZone, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    waste_collectors = models.ManyToManyField(WasteCollector)

    class Meta:
        verbose_name_plural = " Waste Schedules"

    def __str__(self):
        return f"{self.pickup_zone.name} - {self.date} - {self.start_time} - {self.end_time}"


class Resident(models.Model):
    """
    Model for residents.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name_plural = "Residents"

    def __str__(self):
        return self.user.email
