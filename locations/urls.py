from django.conf.urls.defaults import *

# Just a few url's. One for the new form and one for displaying checkins of the user and one for getting the search result
# and then checkin in to that place.

urlpatterns = patterns('',
    url(r'^$', 'locations.views.your_locations', name='loc_yours'),
    url(r'^new/$', 'locations.views.new', name='loc_new'),
    url(r'^checkin/$', 'locations.views.checkin', name='loc_checkin'),
    url(r'^friends/checkins/$', 'locations.views.friends_checkins', name='loc_friends'),
    url(r'^nearby/checkins/$', 'locations.views.nearby_checkins', name='loc_nearby'),
)
