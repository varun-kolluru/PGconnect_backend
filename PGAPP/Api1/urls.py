from django.urls import path
from . import views

urlpatterns = [
    path("test",views.Test),
    path("test2",views.Test2),

    path("",views.index),
    
    path("signup",views.UserRegister),
    path("signin",views.UserLogin),
    path("token_update",views.token_update_view),
    path("verify_otp",views.verify_otp_view),
    path("send_mail",views.send_mail_view),


    path("Pg_add",views.Pg_add_view),
    path("pg_del",views.pg_del_view),
    path("Pg_data",views.Pg_data_view),
    path("gPg_data",views.gPg_data_view),

    path("pgsearch",views.Pgsearch_view),

    path("cguests",views.cguests_view),
    path("capchange",views.capchange_view),

    path("addguest",views.addguest_view),
    path("delguest",views.delguest_view),
    path("guest_phn",views.guest_phn_view),

    path("pg_members",views.pg_members_view),
    path("pg_ownername",views.pg_ownername_view),

    path("paymentadd",views.paymentadd_view),
    path("paymentreqs",views.paymentreqs_view),
    path("payment_statuschange",views.payment_statuschange_view),
    path("payment_guest",views.payment_guest_view),
    path("all_payments",views.all_payments_view),

    path("availablerooms",views.availablerooms_view),
    path("questions",views.questions_view),
    path("chat_cache_clear",views.chat_cache_clear_view),
    path("group_notifications",views.group_notifications_view)
]