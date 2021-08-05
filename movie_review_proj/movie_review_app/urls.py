from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name="home_view"),
    path('register/', views.register_view, name="register_view"),
    path('login/', views.login_view, name="login_view"),
    path('profile/', views.profile_view, name="profile_view"),
 

    path('movies/', views.movie_listing_view, name="movie_listings"),  
    path('add-movie/', views.add_movie, name='add_movie'),
    path('view-movie/<int:id_movie>', views.view_movie_view, name='view_movie_view'),
    path('edit-movie/<int:id_movie>/', views.edit_movie_view, name='edit_movie_view'),
    path('edit-view/<int:id_movie>', views.edit_view_option, name='edit_or_detail_view'),
    
    path('log-out/', views.log_out, name="log_out"),
    path('profile/contact-update/',views.contact_update, name='contact_update'),
    path('profile/address-update/',views.profile_update, name='profile_update'),
    
    path('delete-movie/<int:id_delete>/', views.delete_movie, name='delete_movie'),
    path('add-like/<int:id_like>/', views.add_like, name='like'),
    path('remove-like<int:un_like>/', views.remove_like, name='un_like'),


]