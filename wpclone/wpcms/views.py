from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse,HttpResponseRedirect
from django.views.decorators .csrf import csrf_exempt
from django.contrib.auth.hashers import make_password,check_password
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.decorators import permission_required
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import json
import re
import datetime
# regular expression for field validation
re_email = re.compile(r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*")
re_password = re.compile(r"[a-zA-Z0-9_]*([a-zA-Z][0-9]|[0-9][a-zA-Z])[a-zA-Z0-9_]*$")

#import django apps
from wpcms.models import WPUser, WPUserMeta, WPPosts, WPTerms, WPOptions, WPTermTaxonomy, WPTermRelationships
from wpcms.method import utilities

def index(request):
    # return render_to_response("menu.html", {}, RequestContext(request))
    return HttpResponse("Hello World")

@login_required(login_url='login')
def admin_index_view(request):
    """
    Load admin interface
    """
    # Get total user count to be displayed on dashboard
    total_users = User.objects.all().distinct().count()
    return render_to_response("admin/index.html", {'total_users': total_users}, RequestContext(request))

@login_required(login_url='login')
def create_user(request):
    """
    Create new user
    """
    error = []
    errors = dict()
    data = dict()
    roles = Group.objects.all()
    data['roles'] = roles
    if request.POST:
        json_data_obj = json.loads(request.POST.get('create_user'))
        username = json_data_obj.get('wp_username')
        email = json_data_obj.get('wp_email')
        first_name = json_data_obj.get('wp_first_name')
        last_name = json_data_obj.get('wp_last_name')
        website = json_data_obj.get('wp_website')
        password = json_data_obj.get('wp_password')
        re_confirm_password = json_data_obj.get('wp_repeat_password')
        # TODO:Implement send password through email
        send_password = json_data_obj.get('wp_send_password')
        role = json_data_obj.get('wp_role')

        if not username:
            error.append(1)
        if not re_email.search(email):
            error.append(2)
        if not (password == re_confirm_password and len(password) > 6):
            error.append(3)
        if User.objects.filter(username=username).exists():
            error.append(4)
        if not error:
            try:
                # save user detail in WPUser
                user_obj = User()
                user_obj.username = username
                user_obj.email = email
                user_obj.first_name = first_name
                user_obj.last_name = last_name
                user_obj.set_password(password)
                user_obj.save()
                wp_user_obj = WPUser()
                wp_user_obj.user = user_obj
                if first_name and  last_name:
                    wp_user_obj.display_name = "%s %s" % (first_name, last_name)
                else:
                    wp_user_obj.display_name = username
                wp_user_obj.user_url = website
                wp_user_obj.role_id = role
                wp_user_obj.save()
            except Exception as e:
                print e
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))
    return render_to_response("admin/users/new_user.html", data, RequestContext(request))


def login_view(request):
    """
    Login form
    """
    errors = []
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        # error for server side validation
        if not username:
            errors.append(1)
        if not password:
            errors.append(2)
        if not errors:
            user = auth.authenticate(username=username,password=password)
            if user is not None:
                auth.login(request,user)
                if user.is_active and request.user.is_authenticated():
                    return HttpResponseRedirect('/admin/index/')
            else:
                errors.append(3)
    return render_to_response('admin/login.html',{'errors':errors},RequestContext(request))


def admin_user(request):
    return render_to_response('demo.html',{},RequestContext(request))


def logout_user(request):
    """
    Logout functionality
    when it is called ,it will vanishes session
    """
    auth.logout(request)
    request.session.flush()
    return HttpResponseRedirect(reverse('login'))


@login_required(login_url='login')
@csrf_exempt
def all_pages(request):
    """
    all Pages
    """

    print 'ssdfsdfgsfsd'
    data = dict()
    all_pages_set = None
    published_count = WPPosts.objects.filter(post_status = 'publish')
    month_year_value = request.GET.get("month_year_value") or None
    published_status = request.GET.get("published_status") or None
    if published_status:
        all_pages_set = WPPosts.objects.filter(post_status = 'publish')
    elif not month_year_value:
        # Not found month_year_value in query string
        all_pages_set = WPPosts.objects.all()
    else:
        # Found month_year_value in query string
        month_year_seperated = month_year_value.split(" ")
        month = month_year_seperated[0]
        year = month_year_seperated[1]
        all_pages_set = WPPosts.objects.filter(Q(post_date__month=month) and Q(post_date__year=year))
    data['all_pages_set'] = all_pages_set
    data['published_count'] = published_count

    # Set of "Month Year" to be listed in Filter dropdown
    month_year_set = set([str(page.post_date.strftime("%B")) + " " + str(page.post_date.year) for page in all_pages_set])
    data['month_year_set'] = month_year_set
    return render_to_response('admin/pages/all_pages.html', data, RequestContext(request))


@login_required(login_url='login')
def general_setting(request):
    """
    general settings
    """
    error = []
    errors = dict()
    data = dict()
    date = datetime.datetime.now()
    roles = Group.objects.all()
    week_days = {'Sunday':'Sunday','Monday':'Monday','Tuesday':'Tuesday',
                 'Wednesday':'Wednesday','Thursday':'Thursday','Friday':'Friday','Saturday':'Saturday'}
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value
    data['date'] = date
    data['roles'] = roles
    data['week_days'] = week_days
    if request.POST:
        json_data_objs = json.loads(request.POST.get('general_setting'))
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')
        home = json_data_objs.get('home')
        siteurl = json_data_objs.get('siteurl')
        admin_email = json_data_objs.get('admin_email')
        users_can_register = json_data_objs.get('users_can_register')
        if users_can_register is None:
            json_data_objs.update({'users_can_register':'None'})
        if not home:
            error.append(1)
        if not siteurl:
            error.append(2)
        if not re_email.search(admin_email):
            error.append(3)
        if not error:

            try:
                # save user detail in WPOptions
                for key,val in json_data_objs.items():
                    created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                    created_obj.option_value = val
                    created_obj.autoload = 'yes'
                    created_obj.save()
            except Exception as e:
                print e
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))
    return render_to_response('admin/settings/general.html',data,RequestContext(request))


@login_required(login_url='login')
def media_setting(request):
    data = dict()
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value

    if request.POST:
        json_data_objs = json.loads(request.POST.get('media_setting'))
        print json_data_objs
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')

        thumbnail_crop = json_data_objs.get('thumbnail_crop')
        uploads_use_yearmonth_folders = json_data_objs.get('uploads_use_yearmonth_folders')
        print thumbnail_crop,uploads_use_yearmonth_folders
        if thumbnail_crop is None:
            json_data_objs.update({'thumbnail_crop': 'None'})
        if uploads_use_yearmonth_folders is None:
            json_data_objs.update({'uploads_use_yearmonth_folders': 'None'})

        try:
            # save user detail in WPOptions
            for key, val in json_data_objs.items():
                created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                created_obj.option_value = val
                created_obj.autoload = 'yes'
                created_obj.save()
            return HttpResponse('ok')
        except Exception as e:
            print e
            return HttpResponse('error')

    return render_to_response('admin/settings/media_setting.html', data, RequestContext(request))


@login_required(login_url='login')
def writing_setting(request):
    data = dict()
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value

    if request.POST:
        json_data_objs = json.loads(request.POST.get('writing_setting'))
        print json_data_objs
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')
        use_smilies = json_data_objs.get('use_smilies')
        use_balanceTags = json_data_objs.get('use_balanceTags')
        if use_smilies is None:
            json_data_objs.update({'use_smilies': 'None'})
        if use_balanceTags is None:
            json_data_objs.update({'use_balanceTags': 'None'})

        try:
            # save user detail in WPOptions
            for key, val in json_data_objs.items():
                created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                created_obj.option_value = val
                created_obj.autoload = 'yes'
                created_obj.save()
            return HttpResponse('ok')
        except Exception as e:
            print e
            return HttpResponse('error')

    return render_to_response('admin/settings/writing_setting.html', data, RequestContext(request))


@login_required(login_url='login')
def reading_setting(request):
    data = dict()
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value

    if request.POST:
        json_data_objs = json.loads(request.POST.get('reading_setting'))
        print json_data_objs
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')

        blog_public = json_data_objs.get('blog_public')
        if blog_public is None:
            json_data_objs.update({'blog_public': 'None'})

        try:
            # save user detail in WPOptions
            for key, val in json_data_objs.items():
                created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                created_obj.option_value = val
                created_obj.autoload = 'yes'
                created_obj.save()
            return HttpResponse('ok')
        except Exception as e:
            print e
            return HttpResponse('error')

    return render_to_response('admin/settings/reading_setting.html', data, RequestContext(request))


@login_required(login_url='login')
def permalink_setting(request):
    data = dict()
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value

    if request.POST:
        json_data_objs = json.loads(request.POST.get('permalink_setting'))
        print json_data_objs
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')

        try:
            # save user detail in WPOptions
            for key, val in json_data_objs.items():
                created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                created_obj.option_value = val
                created_obj.autoload = 'yes'
                created_obj.save()
            return HttpResponse('ok')
        except Exception as e:
            print e
            return HttpResponse('error')
    return render_to_response('admin/settings/permalink_setting.html',data,RequestContext(request))


@login_required(login_url='login')
def discussion_setting(request):
    data = dict()
    options = WPOptions.objects.all()
    for option in options:
        data[option.option_name] = option.option_value

    if request.POST:
        json_data_objs = json.loads(request.POST.get('discussion_setting'))
        print json_data_objs
        if json_data_objs.has_key('csrfmiddlewaretoken'):
            json_data_objs.pop('csrfmiddlewaretoken')

        default_pingback_flag = json_data_objs.get('default_pingback_flag')
        default_ping_status = json_data_objs.get('default_ping_status')
        default_comment_status = json_data_objs.get('default_comment_status')
        require_name_email = json_data_objs.get('require_name_email')
        comment_registration = json_data_objs.get('comment_registration')
        close_comments_for_old_posts = json_data_objs.get('close_comments_for_old_posts')
        thread_comments = json_data_objs.get('thread_comments')
        page_comments = json_data_objs.get('page_comments')
        comments_notify = json_data_objs.get('comments_notify')
        moderation_notify = json_data_objs.get('moderation_notify')
        comments_moderation = json_data_objs.get('comments_moderation')
        comments_whitelist = json_data_objs.get('comments_whitelist')
        # comment_max_links = json_data_objs.get('comment_max_links')
        show_avatars = json_data_objs.get('show_avatars')

        if default_pingback_flag is None:
            json_data_objs.update({'default_pingback_flag': 'None'})
        if default_ping_status is None:
            json_data_objs.update({'default_ping_status': 'None'})
        if default_comment_status is None:
            json_data_objs.update({'default_comment_status': 'None'})
        if require_name_email is None:
            json_data_objs.update({'require_name_email': 'None'})
        if comment_registration is None:
            json_data_objs.update({'comment_registration': 'None'})
        if close_comments_for_old_posts is None:
            json_data_objs.update({'close_comments_for_old_posts': 'None'})
        if thread_comments is None:
            json_data_objs.update({'thread_comments': 'None'})
        if page_comments is None:
            json_data_objs.update({'page_comments': 'None'})
        if comments_notify is None:
            json_data_objs.update({'comments_notify': 'None'})
        if moderation_notify is None:
            json_data_objs.update({'moderation_notify': 'None'})
        if comments_moderation is None:
            json_data_objs.update({'comments_moderation': 'None'})
        if comments_whitelist is None:
            json_data_objs.update({'comments_whitelist': 'None'})
        # if comment_max_links is None:
        #     json_data_objs.update({'comment_max_links': 'None'})
        if show_avatars is None:
            json_data_objs.update({'show_avatars': 'None'})

        try:
            # save user detail in WPOptions
            for key, val in json_data_objs.items():
                created_obj, status = WPOptions.objects.get_or_create(option_name=key)
                created_obj.option_value = val
                created_obj.autoload = 'yes'
                created_obj.save()
            return HttpResponse('ok')
        except Exception as e:
            print e
            return HttpResponse('error')

    return render_to_response('admin/settings/discussion_setting.html',data,RequestContext(request))



@login_required(login_url='login')
def create_post(request):
    """
    This method is used for creating posts
    """
    data = dict()
    current_date = datetime.datetime.now()
    data.update({'current_date': current_date})
    if request.POST:
        post_title = request.POST.get('post_title_text') or ""
        post_content = request.POST.get('post_content_html') or ""
        print post_title, post_content

        try:
            wpposts_obj = WPPosts()
            wpposts_obj.post_author = request.user
            wpposts_obj.post_title = post_title
            wpposts_obj.post_parent = 0
            wpposts_obj.post_content = post_content
            wpposts_obj.post_type = 'post'
            wpposts_obj.save()
            return HttpResponse(0)
        except Exception as e:
            print 'error', e

    return render_to_response('admin/posts/new_post.html',data,RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def all_post(request):
    """
    all Pages
    """
    data = dict()
    all_posts_set = None
    published_count = WPPosts.objects.filter(post_status='publish')
    month_year_value = request.GET.get("month_year_value") or None
    published_status = request.GET.get("published_status") or None
    if published_status:
        all_posts_set = WPPosts.objects.filter(post_status='publish', post_type='post')
        #for post in all_posts_set:
        #    wptermrelationships = WPTermRelationships.objects.get(id = post.id)
        #    print "inside",wptermrelationships.term_taxonomy_id
    elif not month_year_value:
        # This is the code for getting a name,slug and id of wp_terms table, Need to be
        # uncomment
        all_posts_set = WPPosts.objects.filter(post_type='post')
        #for post in all_posts_set:
        #    wptermrelationships = WPTermRelationships.objects.filter(object_id=int(post.id))
        #    for termrelation in wptermrelationships:
        #        wptermtaxonomy = WPTermTaxonomy.objects.get(id=int(termrelation.term_taxonomy_id_id))
        #        print "inside", wptermtaxonomy.taxonomy
        #        if wptermtaxonomy.taxonomy == 'category':
        #            print "yes this is the category"
        #            terms = WPTerms.objects.get(id=int(wptermtaxonomy.term_id))
        #            print terms.name
        print "yes"
    else:
        # Found month_year_value in query string
        month_year_seperated = month_year_value.split(" ")
        month = month_year_seperated[0]
        year = month_year_seperated[1]
        all_pages_set = WPPosts.objects.filter(Q(post_date__month=month) and Q(post_date__year=year))
    data['all_pages_set'] = all_posts_set
    data['published_count'] = published_count

    # Set of "Month Year" to be listed in Filter dropdown
    #month_year_set = set([str(page.post_date.strftime("%B")) + " " + str(page.post_date.year) for page in all_pages_set])
    #data['month_year_set'] = month_year_set
    return render_to_response('admin/posts/all_posts.html', data, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def create_categories(request):
    """
    create categories
    """
    #categories_name
    error = []
    errors = dict()
    data = dict()
    data['status'] = False
    if request.method == 'GET':
        status = request.GET.get('status')
        data['status'] = status
    category_list = WPTermTaxonomy.objects.filter(taxonomy='category')
    data['category_list'] = category_list
    if request.POST:
        json_data_obj = json.loads(request.POST.get('categories_details'))
        tag_name = json_data_obj.get('tag_name') or None
        tag_slug = json_data_obj.get('tag_slug') or None
        slug = str(tag_slug).lower().replace(' ','-')
        tag_description = json_data_obj.get('tag_description') or None
        parent = json_data_obj.get('parent') or None

        if not tag_slug:
            slug = str(tag_name).lower().replace(' ','-')
        if not tag_name:
            error.append(1)
        if WPTerms.objects.filter(slug=slug).exists():
            error.append(2)
        if not error:
            try:
                # save category detail in WPUser
                category_obj = WPTerms()
                category_obj.name = tag_name
                category_obj.slug = slug
                category_obj.save()
                category_taxonomy_obj = WPTermTaxonomy()
                category_taxonomy_obj.term = category_obj
                category_taxonomy_obj.taxonomy = 'category'
                category_taxonomy_obj.description = tag_description
                if parent:
                    category_taxonomy_obj.parent = WPTerms.objects.get(id=parent)
                category_taxonomy_obj.save()
            except Exception as e:
                print e
                error.append(3)
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))

    return render_to_response('admin/posts/categories.html',data,RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def update_category(request,category_id):
    """
    This will update category
    """
    error = []
    errors = dict()
    data = dict()
    if category_id:
        try:
            category = WPTermTaxonomy.objects.get(term_id=category_id)
            data['category_name'] = category.term.name
            data['category_slug'] = category.term.slug
            data['category_parent'] = category.parent.name
            data['category_description'] = category.description
            data['error'] = False
        except Exception as e:
            data['error'] = True
    category_list = WPTermTaxonomy.objects.filter(taxonomy='category')
    data['category_list'] = category_list
    data['category_id'] = category_id
    if request.POST:
        json_data_obj = json.loads(request.POST.get('categories_details'))
        tag_name = json_data_obj.get('tag_name') or None
        tag_slug = json_data_obj.get('tag_slug') or None
        slug = str(tag_slug).lower().replace(' ','-')
        tag_description = json_data_obj.get('tag_description') or None
        parent = json_data_obj.get('parent') or None

        if not tag_name:
            error.append(1)
        if WPTerms.objects.filter(slug=slug).exclude(id=category_id).exists():
            error.append(2)
        if not error:
            try:
                # save category detail in WPUser
                WPTerms.objects.filter(id=category_id).update(name=tag_name,slug=tag_slug)
                category_obj = WPTermTaxonomy.objects.get(term_id=category_id)
                category_obj.description = tag_description
                category_obj.parent_id = parent
                category_obj.save()
            except Exception as e:
                print e
                error.append(3)
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))
    return render_to_response("admin/posts/update_category.html",data,RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def delete_category(request):
    """
    Delete pages. Must be called from ajax call.
    """
    return_value = 0
    if request.is_ajax():
        list_delete = request.POST.getlist('list_delete[]')
        if WPTermTaxonomy.objects.filter(term_id__in=list_delete).exists():
            WPTermTaxonomy.objects.filter(term_id__in=list_delete).delete()
        if WPTerms.objects.filter(id__in=list_delete).exists():
            WPTerms.objects.filter(id__in=list_delete).delete()
            return_value = 1
        else:
            return_value = 0
        return HttpResponse(return_value)
    else:
        return HttpResponse(return_value)


@login_required(login_url='login')
@csrf_exempt
def tags(request):
    error = []
    errors = dict()
    data = dict()

    if request.method == 'GET':
        status = request.GET.get('status')
        data['status'] = status
    tag_list = WPTermTaxonomy.objects.filter(taxonomy='post_tag')
    data['tag_list'] = tag_list
    if request.POST:
        json_data_obj = json.loads(request.POST.get('tags'))
        tag_name = json_data_obj.get('tag_name') or None
        tag_slug = json_data_obj.get('tag_slug') or None
        slug = str(tag_slug).lower().replace(' ','-')
        tag_description = json_data_obj.get('tag_description') or None
        print "yes"
        if not tag_name:
            error.append(1)
        if WPTerms.objects.filter(slug=slug).exists():
            error.append(2)
        if not error:
            try:
                # save category detail in WPUser
                tag_obj = WPTerms()
                tag_obj.name = tag_name
                tag_obj.slug = slug
                tag_obj.save()
                tag_taxonomy_obj = WPTermTaxonomy()
                tag_taxonomy_obj.term = tag_obj
                tag_taxonomy_obj.taxonomy = 'post_tag'
                tag_taxonomy_obj.description = tag_description
                # tag_taxonomy_obj.parent = WPTerms.objects.get(id=parent)
                tag_taxonomy_obj.save()
            except Exception as e:
                error.append(3)
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))

    return render_to_response('admin/posts/tag.html', data, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def update_tag(request,tag_id):
    """
    This will update category
    """
    error = []
    errors = dict()
    data = dict()
    if tag_id:
        try:
            tag = WPTermTaxonomy.objects.get(term_id=tag_id)
            data['tag_name'] = tag.term.name
            data['tag_slug'] = tag.term.slug
            data['tag_parent'] = tag.parent
            data['tag_description'] = tag.description
            data['error'] = False
        except Exception as e:
            data['error'] = True
    tag_list = WPTermTaxonomy.objects.filter(taxonomy='post_tag')
    data['tag_list'] = tag_list
    data['tag_id'] = tag_id
    if request.POST:
        json_data_obj = json.loads(request.POST.get('tags_details'))
        tag_name = json_data_obj.get('tag_name') or None
        tag_slug = json_data_obj.get('tag_slug') or None
        slug = str(tag_slug).lower().replace(' ','-')
        tag_description = json_data_obj.get('tag_description') or None

        if not tag_name:
            error.append(1)
        if WPTerms.objects.filter(slug=slug).exclude(id=tag_id).exists():
            error.append(2)
        if not error:
            try:
                # save category detail in WPUser
                WPTerms.objects.filter(id=tag_id).update(name=tag_name,slug=tag_slug)
                category_obj = WPTermTaxonomy.objects.get(term_id=tag_id)
                category_obj.description = tag_description
                category_obj.save()
            except Exception as e:
                print e
                error.append(3)
        errors['error_codes'] = error
        return HttpResponse(json.dumps(errors))
    return render_to_response("admin/posts/update_tag.html",data,RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def delete_tag(request):
    """
    Delete pages. Must be called from ajax call.
    """
    return_value = 0
    if request.is_ajax():
        list_delete = request.POST.getlist('list_delete[]')
        print list_delete
        if WPTermTaxonomy.objects.filter(term_id__in=list_delete).exists():
            WPTermTaxonomy.objects.filter(term_id__in=list_delete).delete()
        if WPTerms.objects.filter(id__in=list_delete).exists():
            WPTerms.objects.filter(id__in=list_delete).delete()
            return_value = 1
        else:
            return_value = 0
        return HttpResponse(return_value)
    else:
        return HttpResponse(return_value)


###############################################################################Front End code #########################################
def front_end_base_view(request):
    """
    This is front end index view
    which gives websites home page
    """

    return render_to_response("front_end/front_end_base.html",{},RequestContext(request))


def front_end_index_view(request):
    """
    This is front end index view
    which gives websites home page
    """

    return render_to_response("front_end/index.html",{},RequestContext(request))


def blog_view(request):
    """
    This is front end index view
    which gives websites home page
    """
    data = dict()
    term_id_list = []
    wptermtexonomy_obj = WPTermTaxonomy.objects.filter(taxonomy='category')
    for obj in wptermtexonomy_obj:
        print ">>>>>>>>>>>>>>> : " + str(obj.term)
        wpterms_obj = WPTerms.objects.get(id=int(obj.term.id))
        term_id_list.append(wpterms_obj)
    data.update({'terms': term_id_list})
    wp_post_obj = WPPosts.objects.all()

    paginator = Paginator(wp_post_obj, 2)
    try:
        page = int(request.GET.get("page", '1'))
    except ValueError:
        page = 1

    try:
        post_set = paginator.page(page)
    except (InvalidPage, EmptyPage):
        post_set  = paginator.page(paginator.num_pages)

    data.update({'wp_post': post_set})
    return render_to_response("front_end/blog.html", data, RequestContext(request))


def blog_item(request):
    data = dict()
    post_id = request.GET.get('id') or None

    try:
        post_id = int(post_id)
    except Exception as e:
        return HttpResponseRedirect('/blog/')

    if post_id:
        wp_post_set = WPPosts.objects.filter(id=post_id)
        if wp_post_set:
            data.update({'wp_post_obj': wp_post_set[0]})
            term_id_list = []
            wptermtexonomy_obj = WPTermTaxonomy.objects.filter(taxonomy='category')
            for obj in wptermtexonomy_obj:
                wpterms_obj = WPTerms.objects.get(id=int(obj.term.id))
                term_id_list.append(wpterms_obj)
            data.update({'terms': term_id_list})
        else:
            return HttpResponseRedirect('/blog/')
    else:
        return HttpResponseRedirect('/blog/')
    return render_to_response("front_end/blog_item.html", data, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def upload_media_files(request):
    print "yes getting"

    if request.method == 'POST':
        print "inside"
        filename = request.FILES['file']
        name = filename.name
        # model_file = open('files/'+name,'wb')
        # print model_file
        # for row in filename:
        #     model_file.write(row)
        print "called", name
        return HttpResponse(name)

    return render_to_response('admin/media/upload_media.html', {}, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def media_library(request):

    return render_to_response('admin/media/media_library.html', {}, RequestContext(request))