from django.conf.urls import url, include,re_path

from workflow.views import Index ,TicketCreate,AllTicket,TicketDetail,MyTicket,MyToDoTicket, MyRelatedTicket,TicketDetailApi,TicketFlowStep,TicketFlowlog,TicketTransition,GetUserName,TicketFieldList,TicketDownload,DownloadTicketData,MyAllTicket,MyUserAdminWorkflows,TicketAccept,GetRolesUsers# , TicketDetail, TicketCreate

urlpatterns = [
    re_path(r'^$', Index.as_view(), name='workflow-index'),
    re_path(r'^my/$', MyTicket.as_view(), name='ticket-my'),
    re_path(r'^mytodo/$', MyToDoTicket.as_view(), name='ticket-my-todo'),
    re_path(r'^myrelated/$', MyRelatedTicket.as_view(), name='ticket-my-related'),
    re_path(r'^all/$', AllTicket.as_view(), name='ticket-all'),
    #url(r'^$', WorkflowView.as_view(), name='workflow-all'),
    #url(r'^(?P<workflow_id>[0-9]+)/init_state',
        #WorkflowInitView.as_view(), name='workflow-init'),
    #url(r'^states/(?P<state_id>[0-9]+)', StateView.as_view()),
    re_path(r'^ticket/(?P<ticket_id>[0-9]+)/$',
        TicketDetail.as_view(), name='ticketdetailtable'),
    re_path(r'^api/(?P<ticket_id>[0-9]+)/$',
        TicketDetailApi.as_view(), name='ticketdetail'),
    re_path(r'(?P<ticket_id>[0-9]+)/flowsteps',
        TicketFlowStep.as_view(), name='ticketflowsteps'),
    re_path(r'(?P<ticket_id>[0-9]+)/flowlogs',
        TicketFlowlog.as_view(), name='ticketflowlogs'),
    re_path(r'(?P<ticket_id>[0-9]+)/transitions',
        TicketTransition.as_view(), name='tickettranstion'),
    re_path(r'^ticket/(?P<workflow_id>[0-9]+)/new/$',
        TicketCreate.as_view(), name='ticketcreate'),
    re_path(r'^getusername/$',
        GetUserName.as_view(), name='getusername'),
    #add by liro
    re_path(r'^fieldlist/(?P<ticket_id>[0-9]+)/$',
        TicketFieldList.as_view(), name='ticketfieldlist'),
    re_path(r'^download/$', TicketDownload.as_view(), name='ticket-download'),
    re_path(r'^download/(?P<workflow_id>[0-9]+)/$', DownloadTicketData.as_view(), name='downloadticketdata'),
    #################################
    re_path(r'^alltickets/$', MyAllTicket.as_view()),
    re_path(r'^user_admin/$', MyUserAdminWorkflows.as_view()),
    re_path(r'^ticketaccept/(?P<ticket_id>[0-9]+)/$',TicketAccept.as_view(), name='ticketaccept'),
    #此功能为了获取loonflow 数据库中的用户
    re_path(r'^getrolesuser/$',GetRolesUsers.as_view(), name='accountusers'),
#    re_path(r'^getaccountuser/(?P<ticket_id>[0-9]+)/$',GetAccountUsers.as_view(), name='accountusers'),
]
