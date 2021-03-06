"""PairWise URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from rest_framework_jwt.views import obtain_jwt_token
from PairWise_Server import views
from PairWise_Server.settings import MEDIA_ROOT, MEDIA_URL

urlpatterns = [
    url(r'^login/', include('rest_framework.urls')),
    url(r'^login/token/$', obtain_jwt_token),
    url(r'^registration/$', views.RegistrationView.as_view(), name='register'),
    url(r'^tags/$', views.data_tag_root),
    url(r'^tags/language/$', views.LanguageList.as_view(), name='language-list'),
    url(r'^tags/concept/$', views.ConceptList.as_view(), name='concept-list'),
    url(r'^tags/framework/$', views.FrameworkList.as_view(), name='framework-list'),
    url(r'^tags/location/$', views.LocationList.as_view(), name='location-list'),
    url(r'^tags/course/$', views.CourseList.as_view(), name='course-list'),
    url(r'^users/$', views.user_categories_root),
    url(r'^users/msg/$', views.NotificationsByUser.as_view(), name='messages'),
    url(r'^users/profile/$', views.ProfileReader.as_view(), name='profile-view'),
    url(r'^users/profile/map/$', views.ProfilePictureMapper.as_view(), name='profile-map'),
    url(r'^users/profile/new/$', views.ProfileWriter.as_view(), name='profile-view'),
    url(r'^users/search/(?P<course_code>\w{3}\d{3,})$', views.SearchDetails.as_view(), name='user-search'),
    url(r'^users/search/(?P<course_code>\w{3}\d{3,})/results/$', views.SearchList.as_view(), name='search-results'),
    url(r'^users/groups/(?P<course_code>\w{3}\d{3,})', views.GroupForm.as_view(), name='group-former'),
    url(r'^admin/', admin.site.urls),
] + static(MEDIA_URL, document_root=MEDIA_ROOT)
