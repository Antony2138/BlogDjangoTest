from django.urls import path, include

from . import views, views_admin

ajax_urlpatterns = [
    path('available_slots/', views.get_available_slots_ajax, name='available_slots_ajax'),
    path('request_next_available_slot/<int:service_id>/', views.get_next_available_date_ajax,
         name='request_next_available_slot'),

]

admin_urlpatterns = [
    path('', views_admin.show_abilities, name='show_all'),
    path('add-service/', views_admin.add_or_update_service, name='add_service'),

]

urlpatterns = [
    path('request/<int:service_id>/', views.appointment_request, name='appointment_request'),
    path('', views.appointment_request_submit, name='appointment_request_submit'),
    path('ajax', include(ajax_urlpatterns)),
    path('app-admin/', include(admin_urlpatterns), name='app-admin'),

]
