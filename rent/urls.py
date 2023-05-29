from django.urls import path
from django.views.generic.base import RedirectView
from rent import views


urlpatterns = [

    path('home/', views.index),
    path('page/<str:section>/', views.index),
    path('loginPage',views.loginpage),
    path('about/', views.About),
    path('contact/', views.ContactUs),


    path('propertyDetail/', views.PropertyDetail),
    path('allproperty/', views.AllProperty),


    path('load-dists/',views.Districts, name='ajax_load_dists'),
    path('load-city/',views.city, name='ajax_load_city'),
    path('load-location/',views.locations, name='ajax_load_locations'),


    path('ActivateThisRoom/',views.PostActivation.as_view()),
    path('DeactivateThisRoom/',views.PostDeactivation.as_view()),


    path('validationpage/', views.ValidationPage),

    path('Validate/<int:pk>', views.Validate),


    path('DeletePost/<int:pk>', views.DeletePost),

    path('deletePostvalidation/<int:pk>', views.deletePostValidation),


    path('Detail/<int:pk>', views.HouseDetail),


    path('tenantDetail/<int:id>', views.TenantDetail),

    path('houseOwnerDetail/<int:id>', views.HouseOwnerDetail),

    path('generate_pdf_tenant/<int:id>', views.generate_pdf_tenant, name='generate_pdf_tenant'),

    path('generate_pdf_owner/<int:id>', views.generate_pdf_owner, name='generate_pdf_owner'),

    path('agreement_pdf/<int:id>', views.agreement_pdf, name='generate_pdf_agreement'),

    path('UploadHouseDetail/', views.UploadHouseDetail),
    path('UploadRoom', views.UploadRoomsViewSet.as_view({'post':'create'})),
    path('PartialUpdateRoom', views.UploadRoomsViewSet.as_view({'patch':'partial_update'})),
    path('UpdateThisRoom/<int:pk>', views.UpdateRooms),
    path('UpdateRoomMediaFile', views.RoomMediaFileUpdate.as_view({'patch':'partial_update'})),

    path('GetRoomData', views.RoomDataViewSet.as_view()),

    
    path("checkout",views.stripe_checkout),
    
    path("booking_success",views.book_succcess),

    path('', RedirectView.as_view(url='home/'))

]




