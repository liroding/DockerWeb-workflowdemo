from django.views.generic import TemplateView, View, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
try:
    import simplejson as json
except ImportError:
    import json
from django import forms
from django.http import Http404,JsonResponse
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field
from crispy_forms.bootstrap import AppendedText, PrependedText
import datetime
import time
from workflow.apirequest import WorkFlowAPiRequest
from django.contrib.auth.models import User

from django.contrib.auth.decorators import login_required
import logging
import json
import csv
import os,sys 
import re,requests
from django.shortcuts import render,render_to_response

logger = logging.getLogger('django')

#此功能函数是用户都可以获取所有的workflow
#class Index(LoginRequiredMixin, TemplateView):
#    template_name = 'workflow/index.html'
#    def get_context_data(self, **kwargs):
#        context = super(Index, self).get_context_data(**kwargs)
#        #context['workflows'] = Workflow.objects.all()
#        ins = WorkFlowAPiRequest(username=self.request.user.username)
#        status,data = ins.getdata(dict(per_page=20, name=''),method='get',url='/api/v1.0/workflows')
#        if status:
#            context['workflows'] = data['data']['value']
#        print("p2")
#        return context

#修改了url，loonflow 根据url 返回相关的workflow
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/index.html'
    def get_context_data(self, **kwargs):
        context = super(Index, self).get_context_data(**kwargs)
        #context['workflows'] = Workflow.objects.all()
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,data = ins.getdata(dict(per_page=20, name=''),method='get',url='/api/v1.0/workflows/user')
        if status and data['code']!= -1:
            context['workflows'] = data['data']['value']
        else:
            print(data['msg']) 
        return context


class TicketDetail(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/ticketdetail.html'

    def get_context_data(self, **kwargs):
        context = super(TicketDetail, self).get_context_data(**kwargs)
        print("liro-debug p1",context)
        context['ticket_id'] = kwargs.get('ticket_id')
        return context


class TicketCreate(LoginRequiredMixin, FormView):
    template_name = 'workflow/ticketcreate.html'
    success_url = '/'

    def get_form_class(self):
        form_fields = dict()
        workflow_id = self.kwargs.get('workflow_id')

        #get ticket initial data
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata({},method='get',url='/api/v1.0/workflows/{0}/init_state'.format(workflow_id))
        """
        state_result example
            {
              'data': {
                'id': 6,
                'name': '发起人-新建中',
                'creator': 'admin',
                'gmt_created': '2018-05-10 07:34:45',
                'distribute_type_id': 1,
                'transition': [
                  {
                    'transition_name': '提交',
                    'transition_id': 7
                  }
                ],
                'order_id': 1,
                'participant_type_id': 5,
                'type_id': 1,
                'is_hidden': False,
                'field_list': [
                  {
                    'boolean_field_display': {
                      
                    },
                    'order_id': 20,
                    'default_value': None,
                    'field_name': '标题',
                    'field_choice': {
                      
                    },
                    'field_key': 'title',
                    'field_type_id': 5,
                    'field_value': None,
                    'field_attribute': 2,
                    'field_template': '',
                    'description': '工单的标题'
                  },
                  {
                    'boolean_field_display': {
                      
                    },
                    'order_id': 110,
                    'default_value': '请填写申请vpn的理由',
                    'field_name': '申请原因',
                    'field_choice': {
                      
                    },
                    'field_key': 'vpn_reason',
                    'field_type_id': 55,
                    'field_value': None,
                    'field_attribute': 2,
                    'field_template': '',
                    'description': 'vpn申请原因'
                  }
                ],
                'participant': 'creator',
                'sub_workflow_id': 0,
                'workflow_id': 2,
                'label': {
                  
                }
              },
              'msg': '',
              'code': 0
            }
        """
        state_result = state_result['data']
        #set state_result to kwargs to avoid mutiple time to obtain ticket info
        self.kwargs.update({'state_result':state_result})

        if isinstance(state_result, dict) and 'field_list' in state_result.keys():
            class DynamicForm(forms.Form):
                def __init__(self, *args, **kwargs):
                    self.helper = FormHelper()
                    self.helper.form_class = 'form-horizontal'
                    self.helper.label_class = 'col-md-2'
                    self.helper.field_class = 'col-md-8'
                    # DictionaryField bug
                    self.helper.layout = Layout(
                        *[Div(field['field_key'], css_class='form-group') for field in state_result['field_list']])
                    super(DynamicForm, self).__init__(*args, **kwargs)

            for field in state_result['field_list']:
                FIELD_TYPE_STR = 5  # 字符串类型
                FIELD_TYPE_INT = 10  # 整形类型
                FIELD_TYPE_FLOAT = 15  # 浮点类型
                FIELD_TYPE_BOOL = 20  # 布尔类型
                FIELD_TYPE_DATE = 25  # 日期类型
                FIELD_TYPE_DATETIME = 30  # 日期时间类型
                FIELD_TYPE_RADIO = 35  # 单选框
                FIELD_TYPE_CHECKBOX = 40  # 多选框
                FIELD_TYPE_SELECT = 45  # 下拉列表
                FIELD_TYPE_MULTI_SELECT = 50  # 多选下拉列表
                FIELD_TYPE_TEXT = 55  # 文本域
                FIELD_TYPE_USERNAME = 60  # 用户名，前端展现时需要调用方系统获取用户列表。loonflow只保存用户名
                if field['field_type_id'] == 5:
                    form_fields[field['field_key']] = forms.CharField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                                                                          'required': field['description']},
                                                                      widget=forms.TextInput(attrs={'placeholder': field['field_name']}))
                elif field['field_type_id'] in [10, 15]:
                    form_fields[field['field_key']] = forms.IntegerField(help_text=field['description'], label=field['field_name'],
                                                                         required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                         error_messages={
                        'required': field['description']},
                        widget=forms.NumberInput(attrs={'placeholder': field['field_name']}))
                elif field['field_type_id'] == 20:
                    form_fields[field['field_key']] = forms.BooleanField(help_text=field['description'], label=field['field_name'],
                                                                         required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                         error_messages={'required': field['description']})
                elif field['field_type_id'] == 25:
                    form_fields[field['field_key']] = forms.DateField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                        'required': field['description']},
                        widget=forms.DateInput(attrs={'placeholder': field['field_name'], 'class': 'dateinput'}))
                elif field['field_type_id'] == 30:
                    form_fields[field['field_key']] = forms.DateTimeField(help_text=field['description'], label=field['field_name'],
                                                                          required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                          error_messages={
                        'required': field['description']},
                        widget=forms.DateTimeInput(attrs={'placeholder': field['field_name'], 'class': 'datetimeinput'}))
                elif field['field_type_id'] in [35, 45]:
                    form_fields[field['field_key']] = forms.ChoiceField(help_text=field['description'], label=field['field_name'],
                                                                        required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                        error_messages={
                        'required': field['description']}, choices=[(k, v) for k, v in field['field_choice'].items()])
                elif field['field_type_id'] in [40, 50]:
                    form_fields[field['field_key']] = forms.MultipleChoiceField(help_text=field['description'], label=field['field_name'],
                                                                                required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                                error_messages={
                        'required': field['description']}, choices=[(k, v) for k, v in field['field_choice'].items()])
                elif field['field_type_id'] == 55:
                    form_fields[field['field_key']] = forms.CharField(help_text=field['description'], label=field['field_name'],
                                                                      required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                      error_messages={
                        'required': field['description']},
                        widget=CKEditorUploadingWidget(attrs={'placeholder': field['field_name'], 'cols': 20, 'rows': 10}))
                elif field['field_type_id'] == 60:
                    form_fields[field['field_key']] = forms.ChoiceField(help_text=field['description'], label=field['field_name'],
                                                                        required=True if field['field_attribute'] == 2 else False, initial=field['default_value'],
                                                                        error_messages={
                        'required': field['description']}, choices=[(i.username,i.username) for i in User.objects.all()])
                # handle read only field
                if field['field_attribute'] == 1:
                    form_fields[field['field_key']
                                ].widget.attrs['disabled'] = 'disabled'
        else:
            raise Http404()
        return type('DynamicItemsForm', (DynamicForm,), form_fields)

    def get_context_data(self, **kwargs):
        context = super(TicketCreate, self).get_context_data(**kwargs)
        context['workflow_id'] = self.kwargs.get('workflow_id')
        state_result = self.kwargs.get('state_result',None)
        context['state_result'] = state_result
        #context['msg'] = msg
        if isinstance(state_result, dict) and 'field_list' in state_result.keys() and len(state_result['field_list']) == 0:
            context['noform'] = True
        if isinstance(state_result, dict) and 'transition' in state_result.keys():
            context['buttons'] = state_result['transition']
        return context

    def form_valid(self, form):
        # save ticket
        if 'transition_id' in form.data.keys():
            transition_id = form.data['transition_id']
            form_data = form.cleaned_data
            form_data['transition_id'] = int(transition_id)
            # form_data['username'] = self.request.user.username
            form_data['workflow_id'] = int(self.kwargs.get('workflow_id'))
            for key, value in form_data.items():
                if isinstance(value, datetime.datetime):
                    form_data[key] = form.data[key]
            #for test only
            ins = WorkFlowAPiRequest(username=self.request.user.username)
            status,state_result = ins.getdata(data=form_data,method='post',url='/api/v1.0/tickets')
            # if new_ticket_result:
            # code, data = 0, {'ticket_id': new_ticket_result}
            # else:
            # code, data = -1, {}
        return super().form_valid(form)


class MyTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/my.html'

    def get_context_data(self, **kwargs):
        context = super(MyTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters=dict(category='owner',per_page=100),method='get',url='/api/v1.0/tickets')
        if status and state_result['code']!=-1:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context

#设置一页获取100笔ticket 记录
class MyToDoTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/mytodo.html'

    def get_context_data(self, **kwargs):
        context = super(MyToDoTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters=dict(category='duty',per_page=100),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and isinstance(state_result['data'],dict) and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class MyRelatedTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/myrelated.html'

    def get_context_data(self, **kwargs):
        context = super(MyRelatedTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters=dict(category='relation',per_page=100),method='get',url='/api/v1.0/tickets')
        if status and state_result['code']!=-1:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class AllTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/allticket.html'

    def get_context_data(self, **kwargs):
        context = super(AllTicket, self).get_context_data(**kwargs)
        request_data = self.request.GET
        #filter ticket in the future if necessary
        sn = request_data.get('sn', '')
        title = request_data.get('title', '')
        username = request_data.get('username', '')
        create_start = request_data.get('create_start', '')
        create_end = request_data.get('create_end', '')
        workflow_ids = request_data.get('workflow_ids', '')
        reverse = int(request_data.get('reverse', 1))
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        # 待办,关联的,创建
        category = request_data.get('category')

        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters=dict(category='all'),method='get',url='/api/v1.0/tickets')
        if status:
            if len(state_result) > 0 and isinstance(state_result,dict) and 'data' in state_result.keys() and 'value' in state_result['data'].keys():
                context['ticket_result_restful_list'] = state_result['data']['value']
        context['msg'] = state_result['msg']
        return context


class TicketDetailApi(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        """
        获取工作流列表
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        name = request_data.get('name', '')
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))
        username = request_data.get('username', '')  # 后续会根据username做必要的权限控制

        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}'.format(self.kwargs.get('ticket_id')))
        print("[liro-debug] p3",state_result)
        return JsonResponse(data=state_result)

    def patch(self,request,*args,**kwargs):
        json_str = request.body.decode('utf-8')
        request_data_dict = json.loads(json_str)
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},data=request_data_dict,method='patch',url='/api/v1.0/tickets/{0}'.format(self.kwargs.get('ticket_id')))
        #handle message bug
        return JsonResponse(state_result)

class TicketFlowStep(LoginRequiredMixin,View):
    """
    工单流转step: 用于显示工单当前状态的step图(线形结构，无交叉)
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get(
            'username', request.user.username)  # 可用于权限控制
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}/flowsteps'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

class TicketFlowlog(LoginRequiredMixin,View):
    """
    工单流转记录
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get(
            'username', request.user.username)  # 可用于权限控制
        per_page = int(request_data.get('per_page', 10))
        page = int(request_data.get('page', 1))

        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}/flowlogs'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)

class TicketTransition(LoginRequiredMixin,View):
    """
    工单可以做的操作
    """

    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get('username', '')
        if not username:
            return api_response(-1, '参数不全，请提供username', '')
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}/transitions'.format(self.kwargs.get('ticket_id')))
        return JsonResponse(data=state_result)


class GetUserName(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        user_id = request.GET.get('user_id')
        try:
            data = User.objects.all(id=user_id).username
        except:
            data = None
        return JsonResponse(data={'username':data})
#add by liro
class TicketFieldList(LoginRequiredMixin,View):
    def get(self, request, *args, **kwargs):
        """
        获取工单所有字段信息
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        request_data = request.GET
        ticket_id = kwargs.get('ticket_id')
        username = request_data.get(
            'username', request.user.username)  # 可用于权限控制
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,basefieldlist_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}/fieldlist'.format(self.kwargs.get('ticket_id')))
#        logger.info('d1')
#        logger.info(basefieldlist_result)
#        logger.info('d2')
        print(basefieldlist_result)
        return JsonResponse({'value':basefieldlist_result})
#add by liro
#此功能返回各workflow对应的下载链接
class TicketDownload(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/ticketdownload.html'
    def get_context_data(self, **kwargs):
        context = super(TicketDownload, self).get_context_data(**kwargs)
        #context['workflows'] = Workflow.objects.all()
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,data = ins.getdata(dict(per_page=20, name=''),method='get',url='/api/v1.0/workflows')
        if status and data['code']!=-1:
            context['workflows'] = data['data']['value']
        return context

class DownloadTicketData(LoginRequiredMixin, TemplateView):
    #将handledata(为Dict数据格式) 数据剥掉,获取自己想要的数据然后封装
    #template_name = 'workflow/test.html'
    def get(self, request, *args, **kwargs):

        request_data = request.GET
        workflow_id = kwargs.get('workflow_id')
        
        username = request_data.get('username', request.user.username)  # 可用于权限控制
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        #获取workflowid 对应的ticketid 的全部数据，最后输出excel文件
        status,workflowid_ticketid_result = ins.getdata(parameters={},method='get',url='/api/v1.0/workflows/{0}/download'.format(self.kwargs.get('workflow_id')))
#        logger.info('d1')
        #print(workflowid_ticketid_result)
        data = self.getmykeydata(workflowid_ticketid_result)
        toexceldata = self.perfectdataformat(data)
        return render(request,'workflow/mydownload.html',{'data':json.dumps(toexceldata)})
 
    def getmykeydata(self,handledata):
        _dellistkey = ['field_key','label','order_id','description','field_attribute','boolean_field_display','default_value','field_template']
        _steplog_delkeylist = ['transition','intervene_type_id','id','state','participant_type_id','participant_info','ticket_id']
        _dictdata = handledata
        _listdata = _dictdata['data']
        _targetdata = []
        for i in range(len(_listdata)):
           #筛选需要的key value 然后存放在_targetdata 中,但包括steplog数据
           #所以进行len(_listdata[i])-1 操作
           for j in range(len(_listdata[i])):
              if(j==(len(_listdata[i])-1)):
                 steplog_total = _listdata[i][j]['total']
                 steplog_value = _listdata[i][j]['value']
                 for z in range(len(steplog_value)):
                     for item in _steplog_delkeylist:
                          del steplog_value[z][item]
    
                 _dictsteplog = {}
                 _dictsteplog['suggestion_data'] = steplog_value
                 del _listdata[i][j]    #删除原数据结构
                 _listdata[i].append(_dictsteplog)     #增加筛选完的数据结构
                 #print(_listdata[i])
              else:
                 for key in _dellistkey:
                    del _listdata[i][j][key] 
                 #print( _listdata[i][j])
           _targetdata.append(_listdata[i])


        return _listdata 
      
    def perfectdataformat(self,handledata):
        _listdata = []
        _data = handledata
        #print(_data)
        for i in range(len(_data)):
           _dictdata = {}
           for j in range(len(_data[i])):  #此处_data[i] 仍为list,内部是多个dict

               #此处增加steplog suggestion数据
               #由于一个工单的流转会有多个处理人的suggestion
               #因此,需要做简单的处理才能在excel 显示输出
               if(j==(len(_data[i])-1)):
                    #print(_data[i][j])
                    strdata = ''
                    suggestion_data = _data[i][j]['suggestion_data']
                    for x in range(len(suggestion_data)):
                        strdata = strdata + \
                          '处理人  :'+ suggestion_data[x]['participant'] + '--' \
                          '处理时间:'+ suggestion_data[x]['gmt_created'] + '--' \
                          '处理意见:'+ suggestion_data[x]['suggestion'] + '\r\n'
                   # print(strdata)
                    _dictdata['处理历史记录'] = strdata
               else:
                    #field_type_id==45 属于select item,需要转换
                    if _data[i][j]['field_type_id'] == 45:
                       fieldvalue = _data[i][j]['field_value']
                       _dictdata[_data[i][j]['field_name']] =  _data[i][j]['field_choice'][fieldvalue]
                    else:
                       #_data[i][j] 是一个dict 结构，内部有多个key:value
                       #value = (_data[i][j]['field_value']).decode(encoding='UTF-8')
                       #_dictdata[key] = value 
                       _dictdata[_data[i][j]['field_name']] =  _data[i][j]['field_value']
            
           _listdata.append(_dictdata)
        return _listdata
#-------------------------------------------------------------------#
class MyAllTicket(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/allticket.html'
    def get(self, request, *args, **kwargs):
        request_data = request.GET
        _workflow_ids = request_data.get('workflow_ids', '')
        _search_value = request_data.get('search_value')
        _per_page = int(request_data.get('per_page'))
        _page = int(request_data.get('page'))
        _category = request_data.get('category')
        _from_admin = request_data.get('from_admin')
        _title = request_data.get('title')
        _create_start = request_data.get('create_start')
        _create_end = request_data.get('create_end')
        _pardata = dict(category=_category,per_page=_per_page,page=_page,workflow_ids=_workflow_ids,\
                        search_value = _search_value,from_admin = _from_admin,title = _title,\
                        create_start = _create_start,create_end = _create_end)
        #ins = WorkFlowAPiRequest(username=self.request.user.username)
        #username 必须给admin 才可以获取全部tickets，其他用户无法获取
        ins = WorkFlowAPiRequest(username='admin')
        status,state_result = ins.getdata(parameters=_pardata,method='get',url='/api/v1.0/tickets')
        print(state_result['data']['value'])
        return JsonResponse({'value':state_result})

#获取用户有权限管理的工作流列表
class MyUserAdminWorkflows(LoginRequiredMixin, TemplateView):
    template_name = 'workflow/allticket.html'

    def get(self, request, *args, **kwargs):
        #ins = WorkFlowAPiRequest(username=self.request.user.username)
        #username 必须给admin 才可以获取全部tickets，其他用户无法获取
        ins = WorkFlowAPiRequest(username='admin')
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/workflows/user_admin')
        print(state_result)
        return JsonResponse({'value':state_result})


#多用户模式下,某用户先接单
class TicketAccept(LoginRequiredMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        ticket_id = kwargs.get('ticket_id')
        print('accept')
        print(ticket_id)
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,data = ins.getdata({},method='post',url='/api/v1.0/tickets/{0}/accept'.format(ticket_id))
        print("accept end")
        return JsonResponse(data=data)
        
class GetRolesUsers(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        request_data = request.GET
        ticket_id = int(request_data.get('ticket_id'))
        print('GetAccountUsers')
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata(parameters={},method='get',url='/api/v1.0/tickets/{0}'.format(ticket_id))
        #查找roles id
        rolesid = state_result['data']['value']['state_info']['participant']

        #通过roles id 找users
        print('t2')
        status,data = ins.getdata(dict(per_page=20),method='get',url='/api/v1.0/accounts/roles/{0}/_users'.format(rolesid))
#        status,data = ins.getdata(dict(per_page=20),method='get',url='/api/v1.0/accounts/_users')
        return JsonResponse({'data':data})
        #return JsonResponse({'data':ticket_id})

class DeliverUsers(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        print('DeliverUsers')
        request_data = request.GET
        print(request_data)
        #ticket_id = request_data.get('ticketid')
        
        for item in request_data:
            suggestion = eval(item).get('suggestion')
            ticket_id  = eval(item).get('ticketid')
            from_admin = eval(item).get('from_admin')
            target_username = eval(item).get('target_username')
        _dictdata =  dict(suggestion=suggestion,target_username=target_username,from_admin=from_admin)
        ins = WorkFlowAPiRequest(username=self.request.user.username)
        status,state_result = ins.getdata({},method='post',url='/api/v1.0/tickets/{0}/deliver'.format(ticket_id),data=_dictdata)
        return JsonResponse({'data':state_result})
