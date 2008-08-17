from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from geopy import geocoders  
from locations.models import Location
from locations.forms import *
import datetime

try:
    from notification import models as notification
except ImportError:
    notification = None
    
# Shows the list of locations a user checked in

def your_locations(request):
    user = request.user
    locations = Location.objects.filter(user=user)
    return render_to_response("location/your_locations.html", {"locations": locations}, context_instance=RequestContext(request))

# Gets data from the search form and tries to geocode that location.
# I am passing an invisible checkin form which contains 'value={{ location.place}}' and other attributes
# so that data can be passed back to view. I did n't knew a better way of doing it.

@login_required
def new(request):
    if request.method == 'POST':
         location_form = LocationForm(request.POST)
         if location_form.is_valid():
             y = geocoders.Yahoo('enter_your_yahoo_map_api_key')     # put your yahoo map api here. 
             p = location_form.cleaned_data['place']
             place, (lat, lng) = y.geocode(p)
             location = {'place': place, 'latitude': lat, 'longitude': lng}
             checkin_form = CheckinForm()
             return render_to_response("location/checkin.html", {"location": location, "checkin_form": checkin_form})
    else:
         location_form = LocationForm()
         return render_to_response("location/new.html", {"location_form": location_form})

# When user clicks checkin, we write into the model Location with user, place, latitude and longitude info. Of course ,along with
# the datetime of the checkin.

@login_required
def checkin(request):
    if request.method == 'POST':
        checkin_form = CheckinForm(request.POST)
        if checkin_form.is_valid():
            c = Location(place=checkin_form.cleaned_data['place'], latitude=checkin_form.cleaned_data['latitude'], longitude=checkin_form.cleaned_data['longitude'], user=request.user, time_checkin= datetime.datetime.now())
            c.save()
            return HttpResponseRedirect(reverse('location.views.your_locations'))
    else:
        return HttpResponseRedirect(reverse('location.views.new'))

         