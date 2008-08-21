from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from geopy import geocoders  
from locations.models import Location
from locations.forms import *
import datetime
from urllib2 import HTTPError

try:
    from notification import models as notification
except ImportError:
    notification = None
    
# Shows the list of locations a user checked in

@login_required
def your_locations(request):
    user = request.user
    location_form = LocationForm()
    locations = Location.objects.filter(user=user)
    return render_to_response("locations/your_locations.html", {"locations": locations, "location_form": location_form}, context_instance=RequestContext(request))

# Gets data from the search form and tries to geocode that location.
# I am passing an invisible checkin form which contains 'value={{ location.place}}' and other attributes
# so that data can be passed back to view. I did n't knew a better way of doing it.

@login_required
def new(request):
    if request.method == 'POST':
         location_form = LocationForm(request.POST)
         if location_form.is_valid():
             y = geocoders.Yahoo('your_yahoo_mapapi')     # put your yahoo map api here. This works for localhost:8000
             p = location_form.cleaned_data['place']
             try:
                 (place, (lat, lng)) = list(y.geocode(p, exactly_one=False))[0]      # Actually returns more than one result but I am taking only the first result
             except HTTPError:
                 return render_to_response("locations/new.html", {"location_form": location_form, "message": "Location not found, Try something else."}, context_instance=RequestContext(request))
             location = {'place': place, 'latitude': lat, 'longitude': lng}
             checkin_form = CheckinForm()
             return render_to_response("locations/checkin.html", {"location": location, "checkin_form": checkin_form})
         else:
              return HttpResponseRedirect(reverse('locations.views.your_locations'))
    else:
         return HttpResponseRedirect(reverse('locations.views.your_locations'))

# When user clicks checkin, we write into the model Location with user, place, latitude and longitude info. Of course ,along with
# the datetime of the checkin.

@login_required
def checkin(request):
    if request.method == 'POST':
        checkin_form = CheckinForm(request.POST)
        if checkin_form.is_valid():
            c = Location(place=checkin_form.cleaned_data['place'], latitude=checkin_form.cleaned_data['latitude'], longitude=checkin_form.cleaned_data['longitude'], user=request.user, time_checkin= datetime.datetime.now())
            c.save()
            return HttpResponseRedirect(reverse('locations.views.your_locations'))
    else:
        return HttpResponseRedirect(reverse('locations.views.new'))

         