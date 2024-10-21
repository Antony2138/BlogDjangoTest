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
    path('service-list/', views_admin.get_service_list, name='get_service_list'),
    path('update-service/<int:service_id>/', views_admin.add_or_update_service, name='update_service'),
    path('delete-service/<int:service_id>/', views_admin.delete_service, name='delete_service'),

    # add, show staff member
    path('add-staff-member-info/', views_admin.add_staff_member_info, name='add_staff_member_info'),
    path('staff-list/', views_admin.get_staff_list, name='get_staff_list'),

    # remove staff member
    path('remove-staff-member/<int:staff_user_id>/', views_admin.remove_staff_member, name='remove_staff_member')

]

urlpatterns = [
    path('request/<int:service_id>/', views.appointment_request, name='appointment_request'),
    path('ajax', include(ajax_urlpatterns)),
    path('', include(admin_urlpatterns), name='app-admin'),

]
