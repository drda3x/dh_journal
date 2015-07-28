"""dh_journal URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""

import views
import application.api as api

from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^group/addstudent', api.add_student),
    url(r'^group/editstudent', api.edit_student),
    # url(r'^group/addpass', api.add_pass),
    url(r'^group', views.group_detail_view),
    url(r'^logout', views.user_log_out),
    url(r'^writeoffpass', api.write_off_the_pass),
    url(r'^processlesson', api.process_lesson),
    url(r'^getpasses', api.get_passes),
    url(r'^deletepass', api.delete_pass),
    url(r'^freezepass', api.freeze_pass),
    url(r'^changeowner', api.change_pass_owner),
    url(r'', views.index_view)
]
