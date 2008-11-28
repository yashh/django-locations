# Author : Yashh (www.yashh.com)
# Since I would be just showing a list of checkins, I haven't included any extra
# methods on the model.


from django.db import models
from django.contrib.auth.models import User

class Location(models.Model):
    user = models.ForeignKey(User)
    time_checkin = models.DateTimeField()
    place = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
  
    class Meta:
        ordering = ('-time_checkin',)
        get_latest_by = 'time_checkin'