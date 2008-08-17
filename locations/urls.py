from django.conf.urls.defaults import *

# Just a few url's. One for the new form and one for displaying checkins of the user and one for getting the search result 
# and then checkin in to that place.

urlpatterns = patterns('',
    (r'^$', 'locations.views.your_locations'),
    (r'new/$', 'locations.views.new'),
    (r'checkin/$', 'locations.views.checkin'),
)
