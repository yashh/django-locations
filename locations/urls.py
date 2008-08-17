from django.conf.urls.defaults import *

# Just a few url's. One for the new form and one for displaying checkins of the user and one for getting the search result 
# and then checkin in to that place.

urlpatterns = patterns('',
    (r'^$', 'location.views.your_locations'),
    (r'new/$', 'location.views.new'),
    (r'checkin/$', 'location.views.checkin'),
)
