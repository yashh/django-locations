import geopy.distance
import geopy.units
import datetime

from urllib2 import HTTPError
from geopy import geocoders

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from locations.models import Location
from friends.models import Friendship
from locations.forms import LocationForm, CheckinForm
from django.conf import settings
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured

try:
    from notification import models as notification
except ImportError:
    notification = None

YAHOO_MAPS_API_KEY = None
def lazy_key():
    global YAHOO_MAPS_API_KEY
    if YAHOO_MAPS_API_KEY is not None:
        return YAHOO_MAPS_API_KEY
    try:
        YAHOO_MAPS_API_KEY = getattr(settings, 'YAHOO_MAPS_API_KEY')
        return YAHOO_MAPS_API_KEY
    except AttributeError:
        raise ImproperlyConfigured('django-locations requires a valid ' +
            'YAHOO_MAPS_API_KEY setting.  Please register for a key at ' +
            'https://developer.yahoo.com/wsregapp/ and then insert your key ' +
            'into the settings file.')

# Shows the list of locations a user checked in
def your_locations(request):
    context = {
        'locations': Location.objects.filter(user=request.user),
        'location_form': LocationForm(),
        'YAHOO_MAPS_API_KEY': lazy_key(),
    }
    return render_to_response("locations/your_locations.html",
        context,
        context_instance=RequestContext(request)
    )
your_locations = login_required(your_locations)

# Gets data from the search form and tries to geocode that location.
# I am passing an invisible checkin form which contains
# 'value={{ location.place }}' and other attributes so that data can be passed
# back to the view. I didn't know a better way of doing it.

def new(request):
    context = {'YAHOO_MAPS_API_KEY': lazy_key()}
    if request.method == 'POST':
        location_form = LocationForm(request.POST)
        if location_form.is_valid():
            y = geocoders.Yahoo(lazy_key())
            p = location_form.cleaned_data['place']
            try:
                (place, (lat, lng)) = list(y.geocode(p, exactly_one=False))[0]
                # Actually returns more than one result but I am taking only the
                # first result
            except HTTPError:
                request.user.message_set.create(
                    message=_('Location not found, Try something else.'))
                context['location_form'] = location_form
                return render_to_response("locations/new.html",
                    context,
                    context_instance=RequestContext(request)
                )
            context.update({
                'location': {'place': place, 'latitude': lat, 'longitude': lng},
                'checkin_form': CheckinForm(),
            })
            return render_to_response("locations/checkin.html",
                context,
                context_instance=RequestContext(request)
            )
        else:
            return HttpResponseRedirect(reverse('locations.views.your_locations'))
    else:
        return HttpResponseRedirect(reverse('locations.views.your_locations'))
new = login_required(new)

# When user clicks checkin, we write into the model Location with user, place,
# latitude and longitude info. Of course, along with the datetime of the checkin.

def checkin(request):
    if request.method == 'POST':
        checkin_form = CheckinForm(request.POST)
        if checkin_form.is_valid():
            c = Location(
                place=checkin_form.cleaned_data['place'],
                latitude=checkin_form.cleaned_data['latitude'],
                longitude=checkin_form.cleaned_data['longitude'],
                user=request.user,
                time_checkin=datetime.datetime.now()
            )
            c.save()
            return HttpResponseRedirect(reverse('locations.views.your_locations'))
    else:
        return HttpResponseRedirect(reverse('locations.views.new'))
checkin = login_required(checkin)

def friends_checkins(request):
    user = request.user
    friends = Friendship.objects.friends_for_user(user)
    context = {
        'friends': friends,
        'YAHOO_MAPS_API_KEY': lazy_key(),
    }
    return render_to_response("locations/friends_checkins.html",
        context,
        context_instance=RequestContext(request)
    )
friends_checkins = login_required(friends_checkins)

def nearby_checkins(request, distance=None):
    user = request.user
    context = {'YAHOO_MAPS_API_KEY': lazy_key()}
    if user.location_set.latest():
        place = user.location_set.latest()
        distance = getattr(settings, 'LOCATIONS_DISTANCE', 20)
        queryset = Location.objects.all()
        rough_distance = geopy.units.degrees(
            arcminutes=geopy.units.nm(miles=distance)) * 2
        queryset = queryset.filter(
            latitude__range=(place.latitude - rough_distance,
                place.latitude + rough_distance),
            longitude__range=(place.longitude - rough_distance,
                place.longitude + rough_distance)
        )
        # Filtering the query set with an area of rough distance all the sides
        locations = []
        for location in queryset:
            if location.latitude and location.longitude:
                exact_distance = geopy.distance.distance(
                    (place.latitude, place.longitude),
                    (location.latitude, location.longitude)
                )
                if exact_distance.miles <= distance:
                    locations.append(location)
        queryset = queryset.filter(id__in=[l.id for l in locations])
        context['queryset'] = queryset.exclude(user=request.user)
        return render_to_response("locations/nearby_checkins.html",
            context,
            context_instance=RequestContext(request)
        )
    else:
        request.user.message_set.create(
            message=_("You haven't checked in any location."))
        return render_to_response("locations/nearby_checkins.html",
            context,
            context_instance=RequestContext(request)
        )
nearby_checkins = login_required(nearby_checkins)