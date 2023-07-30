from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, include, reverse_lazy

from watchBlogProject.watch_blog_app.views import HomeView, PostView, register, log_in, log_out, \
    profile_details, profile_edit, PostCreateView, post_edit, PostDeleteView, CategoryCreateView, TagCreateView, \
    comment_edit, CommentDeleteView, ProfileDeleteView, like_post

urlpatterns = [
                  path('', HomeView.as_view(), name='home'),
                  path('accounts/', include([
                      path('register/', register, name='register'),
                      path('login/', log_in, name='login'),
                      path('logout/', log_out, name='logout'),
                      path('profile/<username>/', profile_details, name='profile details'),
                      path('password-reset/', PasswordResetView.as_view(
                          template_name='password-reset.html',
                          email_template_name='password-reset-email.html',
                          subject_template_name='password_reset_subject.txt',
                          success_url='/accounts/password-reset/done/'),
                           name='password reset'
                           ),
                      path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
                          template_name='password-reset-confirm.html',
                          success_url='/accounts/reset/done/'),
                           name='password reset confirm'
                           ),
                      path('reset/done/', PasswordResetCompleteView.as_view(
                          template_name='password-reset-complete.html'),
                           name='password reset complete'
                           ),
                      path('password-reset/done/', PasswordResetDoneView.as_view(
                          template_name='password-reset-done.html'),
                           name='password reset done'
                           ),
                      path('password-change/', PasswordChangeView.as_view(
                          template_name='password-change.html',
                          success_url=reverse_lazy('password change done')),
                           name='password change'),
                      path('password-change/done/', PasswordChangeDoneView.as_view(
                          template_name='password-change-done.html'),
                           name='password change done'),
                  ])),
                  path('profile/edit/<int:profile_id>/', profile_edit, name='profile edit'),
                  path('profile/<int:pk>/delete/', ProfileDeleteView.as_view(), name='profile delete'),
                  path('post/edit/<int:post_id>/', post_edit, name='post edit'),
                  path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post delete'),
                  path('post/', include([
                      path('<int:pk>/<slug:slug>/', PostView.as_view(), name='post'),
                      path('create/', PostCreateView.as_view(), name='post create'),
                  ])),
                  path('category/create/', CategoryCreateView.as_view(), name='category create'),
                  path('tag/create/', TagCreateView.as_view(), name='tag create'),
                  path('comment/edit/<int:comment_id>/', comment_edit, name='comment edit'),
                  path('comment/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment delete'),
                  path('like/<int:post_id>/', like_post, name='like post'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
