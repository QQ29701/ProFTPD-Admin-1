#coding=utf-8
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.core.urlresolvers import reverse
from django import forms
from django.forms import ModelForm
from django.utils import simplejson 
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Select
from django.views.decorators.csrf import csrf_exempt

from proftpd.ftpadmin.lib.view_common import show_items, view_multiple_done, display_confirm_msg, get_model_html_output
from proftpd.ftpadmin.lib.ftp_info import proftpd_ctrls, get_ftp_info
from proftpd.ftpadmin.settings import SITE_INTERFACE
from proftpd.ftpadmin.models.ftpusers import Ftpuser
from proftpd.ftpadmin.models.ftpgroups import  Ftpgroup
from proftpd.ftpadmin.lib.common import initlog


logger2 = initlog()

FTP_SESSION_CLASS_CHOICES = (
    ('intranet', 'intranet'),
    ('eval', 'eval'),
)

def get_all_instance_name(model=None):
    all_name = []
    for instance in model.objects.all():
        all_name.append( instance.__unicode__() )
    return all_name

def get_choices(v_array=[]):
    choices = []
    for v in v_array:
        choices.append( [v, v] )
    return choices




@login_required(redirect_field_name='')
def session(request):

    if request.method == 'POST':
        logger2.info("POSTPOSTPOSTPOST")
        session_type = request.POST.get('session_type', None)
        session_value = request.POST.get('session_value', None)
        logger2.info("session_value = %s , session_type = %s" % (session_value, session_type) )
        exec_status = 'undefined'
        ctrls = proftpd_ctrls()
        if session_type is not None and session_value is not None:
            if session_type == 'user':
                exec_status = ctrls.kick(k_type='user', k_objective=[session_value])
            elif session_type == 'group':
                exec_status = 'undefined action'
            elif session_type == 'class':
                exec_status = ctrls.kick(k_type='class', k_objective=[session_value])

        return HttpResponse(simplejson.dumps({"status": exec_status}, ensure_ascii = False),
                mimetype='application/json')
    
    
    else:
        attrs = {'id':'session_value'}
        class_html = Select(choices=FTP_SESSION_CLASS_CHOICES).render('session_value', '', attrs=attrs).replace('\n', ' ')
    
        FTP_SESSION_USER_CHOICES = get_choices( v_array=get_all_instance_name(model=Ftpuser) )
        user_html = Select(choices=FTP_SESSION_USER_CHOICES).render('session_value', '', attrs=attrs).replace('\n', ' ')
    
        FTP_SESSION_GROUP_CHOICES = get_choices( v_array=get_all_instance_name(model=Ftpgroup) )
        group_html = Select(choices=FTP_SESSION_GROUP_CHOICES).render('session_value', '', attrs=attrs).replace('\n', ' ')
    
        session = {'user':user_html, 'group':group_html, 'class':class_html}
    
        return render_to_response('ftpadmin/ctrl_session.html', { 'session': session} ,context_instance=RequestContext(request))



@login_required(redirect_field_name='')
def ftp_status(request):
    if request.method == "POST":
        ftp_server_info = get_ftp_info()
        return HttpResponse(simplejson.dumps(ftp_server_info,ensure_ascii = False), mimetype="application/json") 
    else:
        return render_to_response("ftpadmin/ftp_status.html", context_instance=RequestContext(request))

