from django.conf import settings
from django.contrib import admin
from django.conf.urls import patterns, include, url

from oscar.app import shop
from oscar.views import handler500, handler404, handler403

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'', include(shop.urls)),
)

if settings.DEBUG:
    # Render statics/media locally
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Allow error pages to be viewed
    urlpatterns += patterns('',
        url(r'^403$', handler403),
        url(r'^404$', handler404),
        url(r'^500$', handler500)
    )

    # Allow FEDs to get arbitrary templates rendered and see a styleguide
    from django.shortcuts import render
    urlpatterns += patterns('',
        url(r'^templates/(?P<template_name>.*)$', render),
        url(r'^styleguide/$', generic.TemplateView.as_view(template_name='styleguide.html'))
    )
