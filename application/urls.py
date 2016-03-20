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

from django.conf import settings
from django.conf.urls import include, url, patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = patterns('', (r'^media\/(?P<path>.*)$',
                                 'django.views.static.serve',
                                 {'document_root': settings.MEDIA_ROOT}),
                           )
urlpatterns += staticfiles_urlpatterns()

urlpatterns += [
    url(r'^admin/?', include(admin.site.urls)),
    url(r'^group/addstudent', api.add_student),
    url(r'^group/editstudent', api.edit_student),
    # url(r'^group/addpass', api.add_pass),
    url(r'^group', views.group_detail_view),
    url(r'^login', views.LoginView.as_view()),
    url(r'^logout', views.user_log_out),
    url(r'^writeoffpass', api.write_off_the_pass),
    url(r'^processlesson', api.process_lesson),
    url(r'^getpasses', api.get_passes),
    url(r'^deletepass', api.delete_lessons),
    url(r'^deletemultypass', api.delete_pass),
    url(r'^freezepass', api.freeze_pass),
    url(r'^changeowner', api.change_pass_owner),
    url(r'^deletestudent', api.delete_student),
    url(r'^getavailiablepasses', api.get_pass_by_owner),
    url(r'^print', views.print_view),
    url(r'^profile', views.user_profile_view),
    url(r'^save_user_data', api.edit_user_profile),
    url(r'^get_comments', api.get_comments),
    url(r'^edit_comment', api.add_or_edit_comment),
    url(r'^delete_comment', api.delete_comment),
    url(r'^restorelesson', api.restore_lesson),
    url(r'writeoffdebt', api.write_off_debt),
    url(r'clubcards', views.club_cards),
    url(r'createmulty', api.create_multipass),
    url(r'restorestudent', api.restore_student),
    url(r'history', views.history_view),
    url(r'changegroup', api.change_group),
    url(r'getmcdetai', api.get_club_card_detail),
    url(r'sampo', views.SampoView.as_view()),
    url(r'mk', views.BonusClassView.as_view()),
    url(r'', views.IndexView.as_view())
]
