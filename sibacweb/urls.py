from django.conf.urls.defaults import patterns, include, url
#from sibacapp.views.contents import home
#from sibacapp.views.authentication import login, register, user_registered, change_password, logout
#from sibacapp.views.settings import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Pages:
    url(r'^$', 'sibacweb.sibacviews.contents.home', name='home'),
    url(r'^about/$', 'sibacweb.sibacviews.contents.about', name='about'),
    url(r'^links/$', 'sibacweb.sibacviews.contents.links', name='links'),
    url(r'^contacts/$', 'sibacweb.sibacviews.contents.contacts', name='contacts'),
    url(r'^user/login/$', 'sibacweb.sibacviews.authentication.login', name='login'),
    url(r'^user/register/$', 'sibacweb.sibacviews.authentication.register', name='register'),
    url(r'^user/user_registered/$', 'sibacweb.sibacviews.authentication.user_registered', name='user_registered'),
    url(r'^user/change_password/$', 'sibacweb.sibacviews.authentication.change_password', name='change_password'),
    url(r'^user/logout/$', 'sibacweb.sibacviews.authentication.logout', name='logout'),
    url(r'^settings/$', 'sibacweb.sibacviews.settings.settings', name='settings'),

    # Ajax requests
    url(r'^ajaxrequest/get_dt_paragraphs$', 'sibacweb.sibacviews.ajaxrequest.get_dt_paragraphs', name='get_dt_paragraphs'),
    url(r'^ajaxrequest/get_dt_fields$', 'sibacweb.sibacviews.ajaxrequest.get_dt_fields', name='get_dt_fields'),
    url(r'^ajaxrequest/validate_search_expression$', 'sibacweb.sibacviews.ajaxrequest.validate_search_expression', name='validate_search_expression'),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
