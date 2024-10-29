from django.urls import path, include

from . import views, views_admin

ajax_urlpatterns = [
    path('available_slots/', views.get_available_slots_ajax, name='available_slots_ajax'),
    path('request_next_available_slot/<int:service_id>/', views.get_next_available_date_ajax,
         name='request_next_available_slot'),
    path('request_staff_info/', views.get_non_working_days_ajax, name='get_non_working_days_ajax'),
]

admin_urlpatterns = [
    path('', views_admin.show_abilities, name='show_all'),

    # add, remove, show, update service
    path('add-service/', views_admin.add_or_update_service, name='add_service'),
    path('service-list/', views_admin.get_service_list, name='get_service_list'),
    path('update-service/<int:service_id>/', views_admin.add_or_update_service, name='update_service'),
    path('delete-service/<int:service_id>/', views_admin.delete_service, name='delete_service'),

    # add, remove, show, update staff member
    path('add-staff-member-info/', views_admin.add_staff_member_info, name='add_staff_member_info'),
    path('staff-list/', views_admin.get_staff_list, name='get_staff_list'),
    path('update-staff-member/<int:user_id>/', views_admin.update_staff_info, name='update_staff_other_info'),
    path('remove-staff-member/<int:staff_user_id>/', views_admin.remove_staff_member, name='remove_staff_member'),

    ###############################

    # show, update, personal info
    path('user-profile/<int:staff_user_id>/', views_admin.user_profile, name='user_profile'),
    path('user-profile/', views_admin.user_profile, name='user_profile'),
    path('update-user-info/<int:staff_user_id>/', views_admin.update_personal_info, name='update_user_info'),
    path('update-user-info/', views_admin.update_personal_info, name='update_user_info'),


    # add, update, delete day off
    path('add-day-off/<int:staff_user_id>/', views_admin.add_day_off, name='add_day_off'),
    path('update-day-off/<int:day_off_id>/', views_admin.update_day_off, name='update_day_off'),
    path('delete-day-off/<int:day_off_id>/', views_admin.delete_day_off, name='delete_day_off'),


    # add, update, delete working hours
    path('delete-working-hours/<int:working_hours_id>/', views_admin.delete_working_hours, name='delete_working_hours'),
    path('update-working-hours/<int:working_hours_id>/', views_admin.update_working_hours, name='update_working_hours'),
    path('add-working-hours/<int:staff_user_id>/', views_admin.add_working_hours, name='add_working_hours'),
]

urlpatterns = [
    path('services/',  views.show_services, name='services'),
    path('request/<int:service_id>/', views.appointment_request, name='appointment_request'),
    path('request-submit/', views.appointment_request_submit, name='appointment_request_submit'),
    path('ajax/', include(ajax_urlpatterns)),
    path('app-admin/', include(admin_urlpatterns), name='app-admin'),

]
