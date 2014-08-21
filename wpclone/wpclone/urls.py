from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()
urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'wpclone.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
    #############################Admin url pattern#######################################################################################################
    url(r'^admin/index/$', 'wpcms.views.admin_index_view', name='admin_index_view'),
    url(r'^admin/login/$', 'wpcms.views.login_view', name='login'),
    url(r'^admin/logout/$', 'wpcms.views.logout_user', name='logout_user'),
    url(r'^admin/forgot-password/$', 'wpcms.views_mac.forgot_password', name='forgot_password'),
    url(r'^admin/reset_password/(?P<token>[\d\w\ \-]+)/(?P<error>[\w\ ]+)/$', 'wpcms.views_mac.reset_password', name="reset_password"),
    #############################Admin Posts url#######################################################################################################
    url(r'^admin/create-post/$', 'wpcms.views.create_post', name='create_post'),
    url(r'^admin/all-post/$', 'wpcms.views.all_post', name='all_posts'),
    url(r'^admin/create-category/$', 'wpcms.views.create_categories', name='create_categories'),
    url(r'^admin/delete-category/$', 'wpcms.views.delete_category', name='delete_category'),
    # url(r'^admin/get_all_children/$', 'wpcms.views.get_all_children', name='category_list'),
    url(r'^admin/update-category/(?P<category_id>[\d]+)/$', 'wpcms.views.update_category', name='update_category'),
    url(r'^admin/tags/$', 'wpcms.views.tags', name='create_tags'),
    url(r'^admin/update-tag/(?P<tag_id>[\d]+)/$', 'wpcms.views.update_tag', name='update_tag'),
    url(r'^admin/delete-tag/$', 'wpcms.views.delete_tag', name='delete_tag'),
    #############################Admin User url#######################################################################################################
    url(r'^admin/create-user/$', 'wpcms.views.create_user', name='create_user'),
    url(r'^admin/admin/$', 'wpcms.views.admin_user', name='admin'),
    url(r'^admin/update-user/(?P<user_id>[\d]+)/$', 'wpcms.views_mac.update_user', name='update_user'),
    url(r'^admin/delete-user/$', 'wpcms.views_mac.delete_user', name='delete_user'),
    url(r'^admin/change-user-role/$', 'wpcms.views_mac.change_user_role', name='change_user_role'),
    url(r'^admin/all-user/$', 'wpcms.views_mac.all_user', name='all_user'),
    ########################Admin Pages url################################################################################################################
    url(r'^admin/pages/all-pages/$', 'wpcms.views.all_pages', name='all_pages'),
    url(r'^admin/pages/delete-user/$', 'wpcms.views_mac.delete_pages', name='delete_pages'),
    url(r'^admin/pages/create-page/$', 'wpcms.views_mac.load_create_page', name='load_create_page'),
    url(r'^admin/pages/new-page/$', 'wpcms.views_mac.create_page', name='create_page'),
    url(r'^admin/pages/update-page/(?P<page_id>[\d]+)/$', 'wpcms.views_mac.update_page', name='update_page'),
    ########################Admin Setting url################################################################################################################
    url(r'^admin/setting/general/$', 'wpcms.views.general_setting', name='general_setting'),
    url(r'^admin/setting/media-setting/$', 'wpcms.views.media_setting', name='media_setting'),
    url(r'^admin/setting/writing-setting/$', 'wpcms.views.writing_setting', name='writing_setting'),
    url(r'^admin/setting/reading-setting/$', 'wpcms.views.reading_setting', name='reading_setting'),
    url(r'^admin/setting/permalink-setting/$', 'wpcms.views.permalink_setting', name='permalink_setting'),
    url(r'^admin/setting/discussion-setting/$', 'wpcms.views.discussion_setting', name='discussion_setting'),
    ########################Admin Media url################################################################################################################
    url(r'^admin/media/upload-media-files/$', 'wpcms.views.upload_media_files', name='upload_media_files'),
    url(r'^admin/media/media-library/$', 'wpcms.views.media_library', name='media_library'),

    ###########################Front End Url#################################################################################################################
    url(r'^base/$', 'wpcms.views.front_end_base_view', name='base_view'),
    url(r'^$', 'wpcms.views.front_end_index_view', name='home'),
    url(r'^blog/$', 'wpcms.views.blog_view', name='blog_view'),
    url(r'^blog-item/$', 'wpcms.views.blog_item', name='blog_item'),
)
