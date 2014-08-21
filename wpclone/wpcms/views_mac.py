# Django core imports
import random
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.models import get_current_site
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse,Http404
from django.views.decorators .csrf import csrf_exempt
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

# Python Core Libs
import json
import re
import logging

# Model imports
from models import WPUser, WPUserMeta, WPPosts
from wpcms.method.utilities import send_password_reset

re_email = re.compile(r"\w+([-+.']\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*")
logger = logging.getLogger(__name__)


def users(request):
    """
    Load users
    """
    data = dict()
    users = WPUser.objects.all()
    data['users'] = users
    return render_to_response("", data, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def delete_user(request):
    """
    Delete user. Must be called from ajax call.
    """
    print "delete_user executed"
    return_value = 0
    if request.is_ajax():
        list_delete = request.POST.getlist('list_delete[]')
        print type(list_delete)
        if WPUserMeta.objects.filter(user_id__in=list_delete).exists():
            WPUserMeta.objects.filter(user_id__in=list_delete).delete()
        if WPUser.objects.filter(user_id__in=list_delete).exists():
            WPUser.objects.filter(user_id__in=list_delete).delete()
        if User.objects.filter(id__in=list_delete).exists():
            User.objects.filter(id__in=list_delete).delete()
            return_value = 1
        else:
            return_value = 0
        return HttpResponse(return_value)
    else:
        return HttpResponse(return_value)


@login_required(login_url='login')
@csrf_exempt
def delete_pages(request):
    """
    Delete pages. Must be called from ajax call.
    """
    return_value = 0
    if request.is_ajax():
        list_delete = request.POST.getlist('list_delete[]')
        print type(list_delete)
        if WPPosts.objects.filter(id__in=list_delete).exists():
            WPPosts.objects.filter(id__in=list_delete).delete()
            return_value = 1
        else:
            return_value = 0
        return HttpResponse(return_value)
    else:
        return HttpResponse(return_value)


@login_required(login_url='login')
@csrf_exempt
def update_user(request,user_id):
    """
    Update user. Must be called from ajax call.
    """
    print user_id
    username_obj = None
    usermeta_obj = None
    data = dict()
    data.update({'user_id':user_id,'usermeta_obj':usermeta_obj,'username_obj':username_obj})
    if user_id:
        try:
            username_obj = User.objects.get(pk=user_id)
            data.update({"username_obj":username_obj})
            usermeta_obj = WPUserMeta.objects.filter(user_id=user_id)
        except User.DoesNotExist:
            raise Http404
        if usermeta_obj:
            for user_meta in usermeta_obj:
                data.update({user_meta.meta_key: user_meta.meta_value})
    if request.POST:
        rich_editing = request.POST.get('rich_editing') or "False"
        comment_shortcuts = request.POST.get('comment_shortcuts') or "False"
        admin_bar_front = request.POST.get('admin_bar_front') or "False"
        user_login = request.POST.get('user_login')
        first_name = request.POST.get('first_name') or ""
        last_name = request.POST.get('last_name') or ""
        nickname = request.POST.get('nickname')
        email = request.POST.get('email') or None
        url = request.POST.get('url') or ""
        display_name = request.POST.get('display_name') or ""
        description = request.POST.get('description') or ""
        new_password = request.POST.get('new_password') or None
        repeat_password = request.POST.get('repeat_password') or None
        data = dict()
        error_codes = []
        data['status'] = 0
        data['error_codes'] = error_codes

        if not nickname:
            error_codes.append(1)
        if not email or not re_email.search(email):
            error_codes.append(2)
        #if not new_password or not repeat_password:
        #    error_codes.append(3)
        #    print "Passwords not found"
        if new_password != repeat_password:
            error_codes.append(4)
        if new_password and len(new_password) < 7:
            error_codes.append(5)



        # if not re_email.search(str(email)):
        #     error_codes.append(5)

        # Check if Error List is empty. If it's empty then only create a user
        if not error_codes:
            user_details_saved = False
            try:
                user = User.objects.get(pk=user_id)
                user.first_name = first_name
                user.last_name = last_name
                if new_password:
                    user.set_password(new_password)
                # user.is_active = True
                user.email = email
                user.save()
                wp_user = WPUser.objects.get(user_id=user.id)
                wp_user.user_nicename = nickname
                wp_user.user_url = url
                wp_user.display_name = display_name
                wp_user.save()
                user_details_saved = True
            except Exception as e:
                print "Error in updating a user :" + str(e)
                user_details_saved = False

            if user_details_saved:

                # rich_editing field
                try:
                    wp_user_meta = WPUserMeta.objects.get(user_id=user_id, meta_key="rich_editing")
                    wp_user_meta.meta_value = rich_editing
                    wp_user_meta.save()
                except ObjectDoesNotExist as e:
                    wp_user_meta = WPUserMeta()
                    wp_user_meta.meta_key = "rich_editing"
                    wp_user_meta.meta_value = rich_editing
                    wp_user_meta.user_id = user_id
                    wp_user_meta.save()

                # comment_shortcuts field
                try:
                    wp_user_meta = WPUserMeta.objects.get(user_id=user_id, meta_key="comment_shortcuts")
                    wp_user_meta.meta_value = comment_shortcuts
                    wp_user_meta.save()
                except ObjectDoesNotExist as e:
                    wp_user_meta = WPUserMeta()
                    wp_user_meta.meta_key = "comment_shortcuts"
                    wp_user_meta.meta_value = comment_shortcuts
                    wp_user_meta.user_id = user_id
                    wp_user_meta.save()

                # admin_bar_front field
                try:
                    wp_user_meta = WPUserMeta.objects.get(user_id=user_id, meta_key="admin_bar_front")
                    wp_user_meta.meta_value = admin_bar_front
                    wp_user_meta.save()
                except ObjectDoesNotExist as e:
                    wp_user_meta = WPUserMeta()
                    wp_user_meta.meta_key = "admin_bar_front"
                    wp_user_meta.meta_value = admin_bar_front
                    wp_user_meta.user_id = user_id
                    wp_user_meta.save()


                # description field
                try:
                    wp_user_meta = WPUserMeta.objects.get(user_id=user_id, meta_key="description")
                    wp_user_meta.meta_value = description
                    wp_user_meta.save()
                except ObjectDoesNotExist as e:
                    wp_user_meta = WPUserMeta()
                    wp_user_meta.meta_key = "description"
                    wp_user_meta.meta_value = description
                    wp_user_meta.user_id = user_id
                    wp_user_meta.save()
        else:
            data['status'] = 1
        json_data = json.dumps(data)
        return HttpResponse(json_data)
    return render_to_response("admin/users/update_user.html", data, RequestContext(request))

@login_required(login_url='login')
def all_user(request):
    """
    This gives you details
    """
    data = dict()
    user_set = User.objects.all()
    roles = Group.objects.all()
    data['user_set'] = user_set
    data['roles'] = roles
    return render_to_response("admin/users/all_users.html", data, RequestContext(request))

@csrf_exempt
def forgot_password(request):
    logger.info("forgot_password view executed")
    error = []
    user_id = None
    if request.POST:
        logger.info("forgot_password view executed")
        forgot_email = request.POST.get('email')
        print "email",forgot_email
        if re_email.search(str(forgot_email)):
            try:
                user_id = User.objects.get(email=forgot_email)
            except User.DoesNotExist as e:
                print "error", e
                error.append('1')
            if user_id:
                try:
                    print "inside try"
                    event = True
                    reset_token = default_token_generator.make_token(user_id)
                    #reset_token = random.randint(1000000000000, 9000000000000)
                    user_obj = WPUser.objects.get(user_id=user_id.id)
                    print user_obj
                    user_obj.user_activation_key = reset_token
                    user_obj.save()
                    send_password_reset(first_name = user_id.first_name,
                                        user_email = [user_id.email],
                                    token = reset_token,
                                    current_site = get_current_site(request))
                    return render_to_response("admin/forgot_password.html",{'error':error,'current_site':get_current_site(request),'token':reset_token,'event':event},context_instance=RequestContext(request))
                except Exception as e:
                    print e
                    error.append('2')
        else:
            error.append('3')

    return render_to_response("admin/forgot_password.html",{'error':error},context_instance=RequestContext(request))


def reset_password(request, token, error):
    errors = []
    print "yes", token,len(token)
    token = token
    if not token:
        errors.append('0')

    if request.POST:
        password = request.POST.get('password') or None
        repeat_password = request.POST.get('Repeat_password') or None
        token = request.POST.get('token') or None
        if not token or not WPUser.objects.filter(user_activation_key=token).exists():
            errors.append('0')
        if password == repeat_password:
            print password, repeat_password
            if len(password) > 6:  # or Check for Password criteria
                try:
                    user_id_obj = WPUser.objects.get(user_activation_key=token)
                    if user_id_obj:
                        user = User.objects.get(id=user_id_obj.user_id)
                        user.set_password(password)
                        user.save()
                        return HttpResponseRedirect("/")
                except:
                    errors.append('0')
            else:
                errors.append('2')
        else:
            errors.append('3')

    return render_to_response("admin/reset_password.html", {'errors': errors, 'token': token}, RequestContext(request))


@login_required(login_url='login')
@csrf_exempt
def change_user_role(request):
    """
    Change user's role. Must be called from ajax call.
    """
    return_value = 0
    if request.is_ajax():
        print "Entered into ajax call"
        list_change = request.POST.getlist('list_change[]')
        role_id = request.POST.get('role_id')
        try:
            WPUser.objects.filter(user_id__in=list_change).update(role=Group.objects.get(pk=role_id))
        except Exception as e:
            print "Error : " + str(e)
        return_value = 1
        print "Reached"
        return HttpResponse(return_value)
    else:
        return HttpResponse(return_value)


@login_required(login_url='login')
@csrf_exempt
def load_create_page(request):
    """
    View to load create new page template
    """
    print "load_create_page called"
    return render_to_response("admin/pages/new-page.html",{},RequestContext(request))
    #return HttpResponse("Not Implemented Yet")


@login_required(login_url='login')
@csrf_exempt
def create_page(request):
    """
    View to create a new page.
    Must be called from ajax call.
    Returns 0 on successfull creation of a page.
    1 otherwise.
    """
    print "create_page called"
    if request.POST:
        return_code = 0
        print "POST found"
        post_content = request.POST.get("post_content_html") or ""
        post_title = request.POST.get("post_title_text") or ""
        post_status = request.POST.get("post_status") or "publish"

        try:
            wp_page = WPPosts()
            wp_page.post_author = request.user
            wp_page.post_content = post_content
            wp_page.post_parent = 0
            wp_page.post_title = post_title
            wp_page.post_status = post_status
            wp_page.post_excerpt = "None"
            wp_page.to_ping = "None"
            wp_page.pinged = "None"
            wp_page.post_content_filtered = "None"
            wp_page.save()
            return_code = 0
        except Exception as e:
            return_code = 1
            print "Error :" + str(e)
            # logger.error("Error in creating page :" + str(e))
        return HttpResponse(return_code)


@login_required(login_url='login')
@csrf_exempt
def update_page(request, page_id):
    """
    View to create a new page.
    Must be called from ajax call.
    Returns 0 on successfull creation of a page.
    1 otherwise.
    """
    print page_id
    post_obj = None
    data = dict()
    data.update({'page_id':page_id,'post_obj':post_obj})
    if page_id:
        try:
            post_obj = WPPosts.objects.get(pk=page_id)
            data.update({"post_obj":post_obj})
        except User.DoesNotExist:
            raise Http404
    if request.POST:
        return_code = 0
        print "POST found"
        post_content = request.POST.get("post_content_html") or ""
        post_title = request.POST.get("post_title_text") or ""
        post_status = request.POST.get("post_status") or "publish"
        try:
            wp_page = WPPosts.objects.get(id=page_id)
            wp_page.post_content = post_content
            wp_page.post_parent = 0
            wp_page.post_title = post_title
            wp_page.post_type = "page"
            # TODO : Fetch comment_status from default_comment_status in WPOptions model
            wp_page.comment_status = "closed"
            # TODO : Fetch ping_status from default_ping_status key in WPOptions model
            wp_page.ping_status = "closed"
            wp_page.menu_order = 0
            wp_page.post_status = post_status
            wp_page.post_excerpt = "None"
            wp_page.to_ping = "None"
            wp_page.pinged = "None"
            wp_page.post_content_filtered = "None"
            wp_page.save()
            return_code = 0
        except Exception as e:
            return_code = 1
            print "Error :" + str(e)
            # logger.error("Error in creating page :" + str(e))
        return HttpResponse(return_code)
    return render_to_response("admin/pages/update-page.html",data,RequestContext(request))