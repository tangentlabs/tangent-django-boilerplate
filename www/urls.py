from django.conf import settings
from django.contrib import admin
from django.conf.urls import patterns, include, url

admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    # Render statics/media locally
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

    # Allow FEDs to get arbitrary templates rendered and see the styleguide and
    # maintenance page.
    from django.shortcuts import render
    from django.views import generic
    urlpatterns += patterns('',
        url(r'^templates/(?P<template_name>.*)$', render),
        url(r'^styleguide/$', generic.TemplateView.as_view(
            template_name='styleguide.html'))
        url(r'^maintenance/$', generic.TemplateView.as_view(
            template_name='maintenance.html'))
    )

    # Do explicit setup of django debug toolbar
    import debug_toolbar
    urlpatterns += patterns(
        '', url(r'^__debug__/', include(debug_toolbar.urls)))
