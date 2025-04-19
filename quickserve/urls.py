from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("run-migrations/", views.run_migrations),
    path("create-admins/", views.create_superusers),
    path("check-user-role/", views.check_user_role, name='check-user-role'),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/',views.about, name='about'),
    path("search/", views.search_sub_services, name="search"),
    path('contact/',views.contact, name='contact'),
    path('blog/', include('blog.urls')),
    path('user/', include('user.urls')),
    path('save-profile-location/', views.save_profile_location, name='save_profile_location'),
    path('save-employee-location/', views.save_employee_location, name='save_employee_location'),
    path('employee/', include('employee.urls')),
    path('get-location/', views.get_location, name='get_location'),
    path('get_employee_location/<int:employee_id>', views.get_employee_location, name = 'get_employee_location'),
    path('booking/', include('booking.urls')),
    path('subservices/<slug:service_slug>', views.subservices, name='subservices'),
    path("update-fcm-token/", views.update_fcm_token, name='update-fcm-token'),
    path('firebase-messaging-sw.js', TemplateView.as_view(
        template_name="firebase-messaging-sw.js",
        content_type='application/javascript'
    )),
    path('track_employee/<int:employee_id>', views.track_employee, name = 'track_employee'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)