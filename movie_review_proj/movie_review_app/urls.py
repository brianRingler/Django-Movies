from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name="home_view"),
    path('register/', views.register_view, name="register_view"),
    path('login/', views.login_view, name="login_view"),
    path('profile/', views.profile_view, name="profile_view"),
 
    path('add-movie/', views.add_movie_view, name='add_movie_view'),
    path('view-movie/<int:id_view>', views.view_movie_view, name='view_movie_view'),
    path('edit-movie/<int:id_edit>/', views.edit_movie_view, name='edit_movie_view'),
    
    
    path('delete-movie/<int:id_delete>/', views.delete_movie, name='delete_movie'),
    path('log-out/', views.log_out, name="log_out"),
    path('profile/contact-update/',views.contact_update, name='contact_update'),
    path('profile/address-update/',views.profile_update, name='profile_update'),

    

]