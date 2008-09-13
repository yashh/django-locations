from django.conf.urls.defaults import *

# Just a few url's. One for the new form and one for displaying checkins of the user and one for getting the search result 
# and then checkin in to that place.

urlpatterns = patterns('',
    url(r'^$', 'locations.views.your_locations', name='your_checkins'),
    (r'^new/$', 'locations.views.new'),
    (r'^checkin/$', 'locations.views.checkin'),
    url(r'^friends/checkins/$', 'locations.views.friends_checkins', name='friends_checkins'),
    url(r'^nearby/checkins/$', 'locations.views.nearby_checkins', name='nearby_checkins'),
)
