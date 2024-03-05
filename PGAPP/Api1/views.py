from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Pgs_Data,Room_Info,Guest_Info,AppUser,Payments
from .serializers import UserRegistrationSerializer,Pgs_Data_serializer,Room_Info_serializer,Guest_Info_serializer,Payments_serializer
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.decorators import permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime,timedelta 
import pyotp
from django.core.cache import cache


##################################################### caching description ##############################
'''
                                         Pgs_Data
caching needed at:-
1.)username
2.)pgid
3.)pgcity

table updates at:-
1.) Add new pgdata

                                         Room_Info
caching needed at:-
1.)pgid 

table updates at:-
1.)pgid, roomno update capacity
2.)Add new roominfo

                                       Guest_Info
caching needed at:-
1.)username
2.)pgid

table updates at:-
1.) add new guest
2.)pgid,roomno,username del guest
3.)pgid,roomno,username update start_date

                                     AppUser
caching needed at:-

table updates at:-


                                     Payments
caching needed at:- 
1.)pgid,active=True,status=1
2.)pgid,room,payer,active=True
3.)pgid,room,payer,active=False

table updates at:-
1.) pgid,roomno,payer,active=True update to active=False
2.) add new payment
3.)pgid,roomno,payer,active=True,status=1 to status=requested_status
                                  
'''
#######################################################

@api_view(['POST','GET'])
#@permission_classes([IsAuthenticated])
#@permission_classes([AllowAny])
def Test(request):
    if request.method in ['POST','GET']:
        secret_key = 'THISSECRETKEY'
        totp = pyotp.TOTP(secret_key,interval=0.001)
        otp=totp.now()
        print(otp)
        return Response({"test":"responded bruh"})
    
@api_view(['POST','GET'])
#@permission_classes([IsAuthenticated])
#@permission_classes([AllowAny])
def Test2(request):
    if request.method in ['POST','GET']:
        for i in ['a'*25]:
            for j in range(50000,70000):
                key=i+str(j)
                value=['pgname',"roomno","start_date","days_stay","fee","penality","username_id"*10]
                cache.set(key,value)
        return Response({"test2":"responded bruh"})
    
def index(request):
    return render(request, 'index.html')
########################################################### caching ########################################
                                      ##### Pgs_Data cache #####
def pg_cache(key,data):
    record=cache.get(key)
    if record!=None:
        record.append(data)
        cache.set(key,record)
                                      ###### Room_Info cache #####
        
def Room_Info_cache1(key,roomno,capacity):        #capacity update
    record=cache.get(key)
    if record!=None:
        for i in range(len(record)):
            if record[i]["roomno"]==roomno:
                record[i]["capacity"]=capacity
        cache.set(key,record)

def Room_Info_cache2(key,data):                   #adding new data
    record=cache.get(key)
    if record!=None:
        record.append(data)
        cache.set(key,record)
                                      ###### Guest_Info cache #####
def Guest_Info_cache1(key,data):           #add new guest
    record=cache.get(key)
    if record!=None:
        record.append(data)
        cache.set(key,record)

def Guest_Info_cache2(key,pgid,roomno,username):
    record=cache.get(key)
    if record!=None:
        record=[i for i in record if (i["pgid"]==pgid and i["roomno"]==roomno and i["username_id"]==username)==False]
        if len(record)==0:
            cache.delete(key)
        else:
            cache.set(key,record)

def Guest_Info_cache3(key,pgid,roomno,username,start_date):
    record=cache.get(key)
    if record!=None:
        for i in range(len(record)):
            if record[i]["pgid"]==pgid and record[i]["roomno"]==roomno and record[i]["username_id"]==username:
                record[i]["start_date"]=start_date
        cache.set(key,record)

                                      ###### payment cache #####
def payments_cache1(key,roomno,username):
    if key[len(key)-5:]=="True":
        other_key=key[:len(key)-5]+"False"
        record1=cache.get(key)
        record2=cache.get(other_key)
        if record2!=None:
            if record1!=None and len(record1)>0:
                record1=record1[-1]
                record2.append(record1)
                cache.set(other_key,record2)
            else:
                cache.delete(other_key)
        
    record=cache.get(key)
    if record!=None:
        record=[i for i in record if (i["roomno"]==roomno and i["payer"]==username)==False]
        if len(record)==0:
            cache.delete(key)
        else:
            cache.set(key,record)

def payments_cache2(key,data):
    record=cache.get(key)
    if record!=None:
        record.append(data)
        cache.set(key,record)

def payments_cache3(key,roomno,username,new_status):
    record=cache.get(key)
    if record!=None:
        if key[-1]=='1':
            record=[i for i in record if (i['payer']==username and i['roomno']==roomno)==False]
        else:
            for i in range(len(record)):
                if record[i]['payer']==username and record[i]['roomno']==roomno:
                    record[i]["status"]=new_status
        cache.set(key,record)


#########################################################  PG views ############################################ 
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Pg_add_view(request):
    if request.method=='POST':
        serialized_item=Pgs_Data_serializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()

        data=dict(serialized_item.validated_data)
        data["id"]=serialized_item.instance.id
        data["username_id"]=request.data["username"]
        data.pop("username")
        pg_cache('Pgs_Data'+data["username_id"],data)
        pg_cache('Pgs_Data'+'id='+str(data["id"]),data)
        pg_cache('Pgs_Data'+'city='+data["city"],data)

        return Response({"id":serialized_item.instance.id})
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Pg_data_view(request):
    if request.method=='POST':
        record=cache.get('Pgs_Data'+request.data["username"])
        if record==None:
            record=list(Pgs_Data.objects.filter(username=request.data["username"]).values())
            cache.set('Pgs_Data'+request.data["username"],record)
        data=[]
        for i in record:
            data.append([i["id"],i["pgname"],i["floors"],i["flats"]])
        return Response(data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def gPg_data_view(request):
    if request.method=='POST':
        record=cache.get('Guest_Info'+request.data["username"])
        if record==None:
            record=list(Guest_Info.objects.filter(username=request.data["username"]).values()) 
            cache.set('Guest_Info'+request.data["username"],record)
        data={}
        for i in record:
            record1=cache.get('Pgs_Data'+'id='+str(i["pgid"]))
            if record1==None:
                record1=list(Pgs_Data.objects.filter(id=i["pgid"]).values())
                cache.set('Pgs_Data'+'id='+str(i["pgid"]),record1)
            for j in record1:
                key=j["id"]
                if key not in data:
                    data[key]=[[j['pgname'],i["roomno"],i["start_date"],i["days_stay"],i["fee"],i["penality"],j["username_id"]]]
                else:
                    data[key].append([j['pgname'],i["roomno"],i["start_date"],i["days_stay"],i["fee"],i["penality"],j["username_id"]])
        return Response(data)
######################################################### Pg_search views ############################################    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def Pgsearch_view(request):
    if request.method=='POST':
        record=cache.get('Pgs_Data'+'city='+request.data["city"])
        if record==None:
            record=list(Pgs_Data.objects.filter(city=request.data["city"]).values())
            cache.set('Pgs_Data'+'city='+request.data["city"],record)
        data=[]
        for i in record:
            lat,long=map(float,i["location"].split(","))
            data.append([i["id"],i["pgname"],lat,long,i["address"],i["username_id"]])
        return Response({"success":data})


#########################################################  cguests views ############################################
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def cguests_view(request):
    if request.method=='POST': 
        record=cache.get('Room_Info'+str(request.data['pgid']))
        if record==None:
            record=list(Room_Info.objects.filter(pgid=request.data['pgid']).values())
            cache.set('Room_Info'+str(request.data['pgid']),record)
        caps=[]
        for i in record:
            caps.append([i["roomno"],i["capacity"]])
        record=cache.get('Guest_Info'+'pgid='+str(request.data["pgid"]))
        if record==None:
            record=list(Guest_Info.objects.filter(pgid=request.data['pgid']).values())
            cache.set('Guest_Info'+'pgid='+str(request.data["pgid"]),record)
        guests=[]
        for i in record:
            guests.append([i["roomno"],i["username_id"],i["start_date"],i["days_stay"],i["fee"],i["penality"]])
        return Response([caps,guests])

#########################################################  Room views ############################################

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def capchange_view(request):  #pgid,roomno,newcapacity
    if request.method=='POST':
        record=Room_Info.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno']).update(capacity=request.data['capacity'])
        Room_Info_cache1('Room_Info'+str(request.data['pgid']),request.data['roomno'],request.data['capacity'])
        if record==0:
            serialized_item=Room_Info_serializer(data=request.data)
            serialized_item.is_valid(raise_exception=True)
            serialized_item.save() 
            data=dict(serialized_item.validated_data)
            Room_Info_cache2('Room_Info'+str(request.data['pgid']),data)
        return Response("capacity updated")
    
#########################################################   Guest info views   #####################################   
def Add_Grpmsg_for_newpgmember(new_member,pgid):
    new_member=new_member+'_'+str(pgid)
    key='grp_notifications'+str(pgid)
    data=cache.get('Guest_Info'+'pgid='+str(pgid))
    if data==None:
        data=list(Guest_Info.objects.filter(pgid=pgid).values())
        cache.set('Guest_Info'+'pgid='+str(pgid),data)
    members={}
    for i in data:
        members[i["username_id"]+"_"+str(pgid)]=members.get(i["username_id"]+"_"+str(pgid),0)+1
    if members[new_member]==1:
        for i in members:
            past_notifications=cache.get(key+i)
            if past_notifications==None:
                past_notifications=[]
            past_notifications.append(["Greet you new PG mate, "+new_member+" just joined this PG 🎉🥳",'nan','grp notification'])
            cache.set(key+i,past_notifications)

@api_view(['GET','POST'])
#@permission_classes([IsAuthenticated])
def addguest_view(request):  #
    if request.method=='POST':
        serialized_item=Guest_Info_serializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()

        data=dict(serialized_item.validated_data)
        data["start_date"]=serialized_item.instance.start_date
        data.pop("username")
        data["username_id"]=request.data["username"]
        Guest_Info_cache1('Guest_Info'+request.data["username"],data)
        Guest_Info_cache1('Guest_Info'+'pgid='+str(request.data["pgid"]),data)
        Add_Grpmsg_for_newpgmember(data["username_id"],request.data["pgid"])
        data=[data["roomno"],data['username_id'],data["start_date"],data["days_stay"],data["fee"],data["penality"]]
        return Response({'guest':data})

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def delguest_view(request):
    if request.method=='POST':
        Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['username'],active=True).update(active=False)
        payments_cache1('Payments'+str(request.data['pgid'])+'1',request.data["roomno"],request.data["username"])
        payments_cache1('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['username']+"True",request.data["roomno"],request.data["username"])
        Guest_Info.objects.filter(pgid=request.data["pgid"],roomno=request.data["roomno"],username=request.data["username"]).delete()
        Guest_Info_cache2('Guest_Info'+request.data["username"],request.data["pgid"],request.data["roomno"],request.data["username"])
        Guest_Info_cache2('Guest_Info'+'pgid='+str(request.data["pgid"]),request.data["pgid"],request.data["roomno"],request.data["username"])
        return Response({'success':'Guest Info Deleted'})
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def guest_phn_view(request):  #
    if request.method=='POST':
        data=cache.get('AppUser'+request.data["username"])
        if data==None:
            data=list(AppUser.objects.filter(username=request.data["username"]).values())
            cache.set('AppUser'+request.data["username"],data)
        return Response({'success':data[0]["phone"]})

################################################# pg members #######################################################
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def pg_members_view(request):
    if request.method=='POST':
        data=cache.get('Guest_Info'+'pgid='+str(request.data["pgid"]))
        if data==None:
            data=list(Guest_Info.objects.filter(pgid=request.data['pgid']).values())
            cache.set('Guest_Info'+'pgid='+str(request.data["pgid"]),data)
        members=set()
        for i in data:
            members.add(i["username_id"]+"_"+str(request.data['pgid']))
        members=list(members)
        return Response({'members':members})

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def pg_ownername_view(request):
    if request.method=='POST':
        data=cache.get('Pgs_Data'+'id='+str(request.data['pgid']))
        if data==None:
            data=list(Pgs_Data.objects.filter(id=request.data['pgid']).values())
            cache.set('Pgs_Data'+'id='+str(request.data['pgid']),data)
        if len(data)>0:
            owner=data[0]["username_id"]
        return Response({'owner':owner})
        
#################################################  Payments #######################################################
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def paymentadd_view(request):  
    if request.method=='POST':
        Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['payer'],active=True).update(active=False)
        payments_cache1('Payments'+str(request.data['pgid'])+'1',request.data["roomno"],request.data["payer"])
        payments_cache1('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True",request.data["roomno"],request.data["payer"])
        serialized_item=Payments_serializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()

        data=dict(serialized_item.validated_data)
        payments_cache2('Payments'+str(request.data['pgid'])+'1',data)
        payments_cache2('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True",data)

        return Response({'success':'Payments Info Saved'})

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])            #for notifications screen
def paymentreqs_view(request):  
    if request.method=='POST':
        data=cache.get('Payments'+str(request.data['pgid'])+'1')
        if data==None:
            data=list(Payments.objects.filter(pgid=request.data['pgid'],active=True,status=1).values())
            cache.set('Payments'+str(request.data['pgid'])+'1',data)
        ans=[]
        for i in data:
            ans.append([i['roomno'],i['payer'],i['name_in_upi'],i['method'],i['Amount_paid'],i['actual_amount'],i['payment_date']])
        return Response(ans)

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def payment_statuschange_view(request):
    if request.method=='POST':
        updated_records=Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['payer'],active=True,status=1).update(status=request.data['status'])
        payments_cache3('Payments'+str(request.data['pgid'])+'1',request.data['roomno'],request.data['payer'],request.data['status'])
        payments_cache3('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True",request.data['roomno'],request.data['payer'],request.data['status'])
        print("no:of updated records",updated_records)
        return Response("field updated")
    
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def payment_guest_view(request):
    if request.method=='POST':
        pinfo=cache.get('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True")
        if pinfo==None:
            pinfo=list(Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['payer'],active=True).values())
            cache.set('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True",pinfo)
        if len(pinfo)==0:
            status=-1
        else:
            status=pinfo[len(pinfo)-1]['status']
        
        guest=request.data["guest"] #[i["start_date"],i["days_stay"],i["fee"],i["penality"]]
        guest[0]=datetime.fromisoformat(guest[0].rstrip('Z'))
        
        def add_days_to_timestamp(original_timestamp, days_to_add):
            new_datetime = original_timestamp + timedelta(days=days_to_add)
            current_datetime = datetime.now(new_datetime.tzinfo)
            time_difference = new_datetime - current_datetime
            difference_in_days = time_difference.days
            difference_in_hours = time_difference.seconds // 3600
            return difference_in_days, difference_in_hours
        
        days_dif, hours_dif = add_days_to_timestamp(guest[0], guest[1])
        added_penality=0
        if days_dif<0 or hours_dif<0:
            if status==2:
                #update guest_info (new start_date=guest[0]+timedelta(days=guest[1]))
                Guest_Info.objects.filter(pgid=request.data['pgid'],username=request.data["payer"],roomno=request.data["roomno"]).update(start_date=guest[0]+timedelta(days=guest[1]))
                Guest_Info_cache3('Guest_Info'+request.data["payer"],request.data['pgid'],request.data["roomno"],request.data["payer"],guest[0]+timedelta(days=guest[1]))
                Guest_Info_cache3('Guest_Info'+'pgid='+str(request.data["pgid"]),request.data['pgid'],request.data["roomno"],request.data["payer"],guest[0]+timedelta(days=guest[1]))
                Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['payer'],active=True).update(active=False)
                payments_cache1('Payments'+str(request.data['pgid'])+'1',request.data["roomno"],request.data["payer"])
                payments_cache1('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['payer']+"True",request.data["roomno"],request.data["payer"])
                guest[0]=guest[0]+timedelta(days=guest[1])
                status=-1
            else:
                added_penality=-1*((days_dif*24)+(hours_dif))*guest[3]
        return Response({'pstatus':status,'added_penality':added_penality})

@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def all_payments_view(request):
    if request.method=='POST':
        data=cache.get('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['username']+"False")
        if data==None:
            data=list(Payments.objects.filter(pgid=request.data['pgid'],roomno=request.data['roomno'],payer=request.data['username'],active=False).values())
            cache.set('Payments'+str(request.data['pgid'])+str(request.data['roomno'])+request.data['username']+"False",data)
        return Response({'payments':data}) 

 
######################################################## Rooms Available view ##################################################
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def availablerooms_view(request):
    if request.method=='POST':
        record=cache.get('Room_Info'+str(request.data['pgid']))
        if record==None:
            record=list(Room_Info.objects.filter(pgid=request.data['pgid']).values())
            cache.set('Room_Info'+str(request.data['pgid']),record)
        caps={}
        for i in record:
            caps[i["roomno"]]=i["capacity"]
        record=cache.get('Guest_Info'+'pgid='+str(request.data["pgid"]))
        if record==None:
            record=list(Guest_Info.objects.filter(pgid=request.data['pgid']).values())
            cache.set('Guest_Info'+'pgid='+str(request.data["pgid"]),record)
        for i in record:
            caps[i["roomno"]]-=1
        available_rooms=sum(caps.values())
        return Response({'rooms':available_rooms})
######################################################### Cache views ##################################################
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
def questions_view(request):
    if request.method=='POST':
        if 'sending' in request.data['type']:
            if request.data['type']=='guest_sending':
                key='q_'+str(request.data['pgid'])+'_'+request.data['receiver'] 
                pgname=[]
            else:
                pgname=[request.data['pgname']]
                key='q_'+str(request.data['receiver']) 
                sender_key='q_'+str(request.data['pgid'])+'_'+request.data['sender']
                sender_msgs=cache.get(sender_key)
                idx=request.data['index']
                sender_msgs.pop(idx)
                if len(sender_msgs)>0:                                   #clearning replyed msgs from cache
                    cache.set(sender_key,sender_msgs)
                else:
                    cache.delete(sender_key)
                print("owner msgs=",cache.get(sender_key))
            prev_msgs=cache.get(key)
            if prev_msgs==None:
                prev_msgs=[]
            prev_msgs.append([request.data['msg'],request.data['sender']]+pgname)
            cache.set(key,prev_msgs)                                     #adding msgs to cache when sent
            print("messages",cache.get(key))
            return Response({'msg':'sent'})
        if 'receiving' in request.data['type']:
            if request.data['type']=='owner_receiving':
                key='q_'+str(request.data['pgid'])+'_'+request.data['receiver']
            else:
                key='q_'+str(request.data['receiver'])
            msgs=cache.get(key)
            if msgs==None:
                msgs=[]
            return Response({'msg':msgs})
        if request.data['type']=='guest_clear':                         #clearning guest msgs from cache when screen opened
            cache.delete('q_'+str(request.data['receiver']))
            print("cleared")
            return Response({'msg':"cleared"}) 

@api_view(['GET','POST'])     
def chat_cache_clear_view(request):
    if request.method=='POST':
        key,sender=request.data["key"],request.data["sender"]
        receiver_msgs=cache.get(key)
        if receiver_msgs!=None and sender in receiver_msgs:
            receiver_msgs.pop(sender)
            cache.set(key,receiver_msgs)
        return Response({'msg':"cleared"})
    
@api_view(['GET','POST'])  
def group_notifications_view(request):
    if request.method=='POST':
        key='grp_notifications'+str(request.data["pgid"])+request.data["key"]
        data=cache.get(key)
        if data==None:data=[]
        cache.delete(key)
        return Response({'msgs':data})
#########################################################  USER Authentication views ############################################
@api_view(['POST'])
@permission_classes([AllowAny])
def UserLogin(request):
    if request.method=='POST':
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            token = RefreshToken.for_user(user)
            return Response(
                        {'token':str(token.access_token),
                         'refresh_token':str(token),
                         'name': f"{user.fname} {user.lname}",
                         'phone': user.phone,
                         'username': user.username,
                         'email': user.email
                        }
                    )
        else:
            return Response({'error': 'Invalid credentials'})

@api_view(['POST'])
@permission_classes([AllowAny])
def UserRegister(request):
    if request.method=='POST':
        serialized_item=UserRegistrationSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        data=serialized_item.validated_data
        user=AppUser.objects.create_user(data)
        return Response("Registered")
    
@api_view(['POST'])
@permission_classes([AllowAny])
def token_update_view(request):
    if request.method=='POST':
        try:
            token = RefreshToken(request.data["refresh_token"])
            return Response({'token':str(token.access_token),'refresh_token':str(token)})
        except Exception as e:
            return Response({'error':"invalid refresh token"})

        
@api_view(['POST'])
@permission_classes([AllowAny])
def send_mail_view(request):
    if request.method=='POST':
        user=AppUser.objects.filter(email=request.data["email"]).exists()
        if user==False:return Response({"error":"Email not registered"})
        secret_key = 'THISSECRETKEY'
        totp = pyotp.TOTP(secret_key,interval=0.001)
        otp=totp.now()
        #send email
        cache.set('otp_'+request.data["email"],value=otp,timeout=120)  
        return Response({"sent":'done'})

@api_view(['POST'])
@permission_classes([AllowAny])
def verify_otp_view(request):
    if request.method=='POST':
        user=AppUser.objects.get(email=request.data["email"])
        otp=cache.get('otp_'+request.data["email"])
        if otp==None:Response({"otp expired":"otp expired, regenerate otp again"})
        if otp==int(request.data['otp']):
            user.set_password=request.data["pass"]
            user.save()
            return Response({"matched":"done"})
        return Response({"wrong otp":"wrong otp"})
        

###################################################################################   