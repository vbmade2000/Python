# Django imports
from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.models import Permission,Group
from django.utils.timezone import utc
# Core Python imports
import datetime


class WPUser(models.Model):
    """
    User model to store user details
    WordPress Table : wr_users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_nicename = models.CharField(max_length=50)
    user_url = models.CharField(max_length=100)
    user_activation_key = models.CharField(max_length=60)
    user_status = models.IntegerField(default=0)
    display_name = models.CharField(max_length=250)
    role = models.ForeignKey(Group)


class WPUserMeta(models.Model):
    """
    Stores user's meta information
    """
    user_id = models.BigIntegerField(default=0)
    meta_key = models.CharField(max_length=255, null=True)
    meta_value = models.TextField()


class WPTerms(models.Model):
    """
    Stores terms
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    term_group = models.BigIntegerField(max_length=10, default=0)


class WPPosts(models.Model):
    """
    Stores posts, pages and menus. Main content table in application
    """
    post_author = models.ForeignKey(User)
    post_date = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
    post_date_gmt = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
    post_content = models.TextField()
    post_title = models.TextField()
    post_excerpt = models.TextField()
    post_status = models.CharField(max_length=20, default='publish')
    comment_status = models.CharField(max_length=20, default='open')
    ping_status = models.CharField(max_length=20, default='open')
    post_password = models.CharField(max_length=20, default="")
    post_name = models.CharField(max_length=200, default="")
    to_ping = models.TextField()
    pinged = models.TextField()
    post_modified = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
    post_modified_gmt = models.DateTimeField(default=datetime.datetime.utcnow().replace(tzinfo=utc))
    post_content_filtered = models.TextField()
    post_parent = models.BigIntegerField()
    guid = models.CharField(max_length=255, default="")
    menu_order = models.IntegerField(default=0)
    post_type = models.CharField(max_length=20, default='post')
    post_mime_type = models.CharField(max_length=100, default="")
    comment_count = models.BigIntegerField(default=0)


class WPPostMeta(models.Model):
    """
    Stores meta information related to posts, pages and menus
    """
    post = models.ForeignKey(WPPosts)
    meta_key = models.CharField(max_length=255)
    meta_value = models.TextField()


class WPOptions(models.Model):
    """
    Stores global application wide settings
    """
    option_name = models.CharField(max_length=64, default='', unique=True)
    option_value = models.TextField()
    autoload = models.CharField(max_length=20, default='yes')


class WPLinks(models.Model):
    """
    Links
    """
    link_ur = models.URLField(default='')
    link_name = models.CharField(max_length=255, default='')
    link_image = models.CharField(max_length=255, default='')
    link_target = models.CharField(max_length=25, default='')
    link_description = models.CharField(max_length=255, default='')
    link_visible = models.CharField(max_length=20, default='Y')
    link_owner = models.ForeignKey(User, default='1')
    link_rating = models.IntegerField(default=0)
    link_updated = models.DateTimeField(default=datetime.datetime.now())
    link_rel = models.CharField(max_length=255, default='')
    link_notes = models.TextField()
    link_rss =  models.CharField(max_length=255, default='')


class WPTermRelationships(models.Model):
    """
    Term Relationship
    """
    object_id =  models.ForeignKey(WPPosts)
    term_taxonomy_id = models.ForeignKey('WPTermTaxonomy')
    term_order = models.IntegerField(default=0)

    class Meta:
        unique_together = (("id", "term_taxonomy_id"),)


class WPTermTaxonomy(models.Model):
    """
    Term Taxonomy
    """
    term = models.ForeignKey(WPTerms, default=0, unique=True, related_name='term')
    taxonomy = models.CharField(max_length=32, default='')
    description = models.TextField(null=True)
    parent = models.ForeignKey(WPTerms, related_name='parent', null=True)
    count = models.BigIntegerField(default=0)

    # def get_all_children(self, include_self=True):
    #     r = []
    #     if include_self:
    #         r.append(self)
    #     for c in WPTermTaxonomy.objects.filter(parent_id=2):
    #         r.append(c.get_all_children(include_self=False))
    #     return r






