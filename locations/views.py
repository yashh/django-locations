from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from geopy import geocoders
import geopy.distance
from locations.models import Location
from friends.models import Friendship
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
             y = geocoders.Yahoo('.Z4iD9nV34EdofUSyd_B5bLj5hrf6wiNszlLacUyxedUanphrJ_ibbMjlntY9eufKwtW')     # put your yahoo map api here. This works for localhost:8000
             p = location_form.cleaned_data['place']
             try:
                 (place, (lat, lng)) = list(y.geocode(p, exactly_one=False))[0]      # Actually returns more than one result but I am taking only the first result
             except HTTPError:
                 return render_to_response("locations/new.html", {"location_form": location_form, "message": "Location not found, Try something else."}, context_instance=RequestContext(request))
             location = {'place': place, 'latitude': lat, 'longitude': lng}
             checkin_form = CheckinForm()
             return render_to_response("locations/checkin.html", {"location": location, "checkin_form": checkin_form}, context_instance=RequestContext(request))
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
        
@login_required
def friends_checkins(request):
    user = request.user
    friends = Friendship.objects.friends_for_user(user)
    return render_to_response("locations/friends_checkins.html", {"friends": friends}, context_instance=RequestContext(request))

@login_required
def nearby_checkins(request, distance=None):
    user = request.user
    if user.location_set.latest:
        place = user.location_set.latest()
        distance = 20                    # Hard coding the radial seach value. TODO: Take as url argument or put a form on the page with js slider
        queryset = Location.objects.all()
        rough_distance = geopy.distance.arc_degrees(arcminutes=geopy.distance.nm(miles=distance)) * 2
        queryset = queryset.filter(
              latitude__range=(place.latitude - rough_distance, place.latitude + rough_distance), 
              longitude__range=(place.longitude - rough_distance, place.longitude + rough_distance)
              )                         # Filtering the query set with an area of rough distance all the sides
        locations = []
        for location in queryset:
          if location.latitude and location.longitude:
            exact_distance = geopy.distance.distance(
                      (place.latitude, place.longitude),
                      (location.latitude, location.longitude)
                      )
            exact_distance.calculate()
            if exact_distance.miles <= distance:
              locations.append(location)

        queryset = queryset.filter(id__in=[l.id for l in locations])
        near_locations = queryset.exclude(user=request.user)
        return render_to_response("locations/nearby_checkins.html", {"queryset": near_locations}, context_instance=RequestContext(request))
    else:
        return render_to_response("locations/nearby_checkins.html", {"message": "You haven't checked in any location."}, context_instance=RequestContext(request))