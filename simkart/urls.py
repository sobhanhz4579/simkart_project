# simkart/urls.py
from django.urls import path
from .views import SimCardListView, SimCardCreateView, CommentListCreateView, RegisterSend, RegisterVerified, \
    ChangePasswordView, LogoutView, SimCardDetailView, LoginSend, LoginVerified, AdminCommentListView, \
    AdminCommentUpdateView, AdminCommentDeleteView, ShareSimCardView, ContactUs, SearchView

app_name = 'simkart'

urlpatterns = [
    path('simcards/', SimCardListView.as_view(), name='simcard-list'),
    path('simcards/create/', SimCardCreateView.as_view(), name='simcard-create'),
    path('simcards/<int:pk>/', SimCardDetailView.as_view(), name='simcard-detail'),
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/admin/', AdminCommentListView.as_view(), name='admin-comment-list'),
    path('comments/admin/<int:pk>/', AdminCommentUpdateView.as_view(), name='admin-comment-update'),
    path('comments/admin/simcard/<int:simcard_id>/', AdminCommentDeleteView.as_view(), name='admin-comment-delete'),
    path('register/send/', RegisterSend.as_view(), name='register_send'),
    path('register/verify/', RegisterVerified.as_view(), name='register_verify'),
    path('login/send/', LoginSend.as_view(), name='login-send'),
    path('login/verify/', LoginVerified.as_view(), name='login-verify'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('simcards/share/<int:pk>/', ShareSimCardView.as_view(), name='simcard-share'),
    path('contact-us/', ContactUs.as_view(), name='contact-us'),
    path('search/', SearchView.as_view(), name='search-view'),
]
