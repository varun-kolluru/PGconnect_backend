import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from datetime import datetime, timedelta


def get_time_ist():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now.strftime("%H:%M")

#redis tip for memory management:-  ref:-https://redis.io/docs/reference/eviction/
#set maxmemory parameter, 
#Eviction policies:-allkeys-lru: Keeps most recently used keys; removes least recently used (LRU) keys when memory is full

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.cur_user = self.scope["url_route"]["kwargs"]["room_name"]   #outer_Varun21+"_pgid", inner_Varun21_pgid, innergpgid (g=group)
        self.room=self.cur_user[6:] 


        await self.channel_layer.group_add(self.room, self.channel_name)

        if self.cur_user[:6]=='outer_':           #if outer then add new connection to online list
            online=cache.get('online')
            if online==None:online=set()  
            online.add(self.room) 
            cache.set('online',online)
        elif self.cur_user[:6]=='inner_':
            online=cache.get('online')           #if inner then check if other user is online for online status  
            if online==None:online=set()
            if self.cur_user[6:] in online:
                online=True
            else:
                online=False  

        await self.accept()

        if self.cur_user[:6]=='outer_':          #if outer then check for past messages and send them
            data=cache.get(self.room)             #{'sender1':[[msg1,ts1],[msg2,ts2]],'sender2':[[msg1,ts1],[msg2,ts2]]}
            if data!=None:             
                await self.send(json.dumps(data))
        elif self.cur_user[:6]=='inner_':
            await self.send(json.dumps({'online_status':online}))   #if inner then send online status
                                          

    async def disconnect(self, close_code):
        # Leave room group
        if self.cur_user[:6]=='outer_':                           #if outer then remove from online and send offline status
            online=cache.get('online')
            online.remove(self.room)
            cache.set('online',online)
            await self.channel_layer.group_send(self.room, {"type": "chat_message" ,"data": {'online_status':False}})

        await self.channel_layer.group_discard(self.room, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)                #{sender:username,msg:msg} or {online_status:true}

        if self.cur_user[:6]=='outer_':              #if outer and online_status in data then send to other user that he is online
            if 'online_status' in data:
                await self.channel_layer.group_send(self.room, {"type": "chat_message" ,"data": data})

        if self.cur_user[:6]=='innerg':
            if 'pgmembers' in data:
                cache.set(self.cur_user[6:],set(data['pgmembers']))   #PG_group_gid
            else:
                online=cache.get('online')
                if online==None:online=set()
                grp_mems=cache.get(self.cur_user[6:])
                grp_online=online.intersection(grp_mems)
                grp_offline=grp_mems-grp_online
                #print('grp mems',grp_mems,'online:-',grp_online,'offline',grp_offline,data)
                for i in grp_offline:
                    past_msgs=cache.get(i)
                    if past_msgs==None:past_msgs={}                 
                    if data['sender'] in past_msgs:
                        past_msgs[data['sender']].append([data['msg'],get_time_ist(),data['sent_by']])   
                    else:
                        past_msgs[data['sender']]=[[data['msg'],get_time_ist(),data['sent_by']]]
                    cache.set(i,past_msgs)
                for i in  grp_online:
                    await self.channel_layer.group_send(i, {"type": "chat_message" ,"data": data})

        if self.cur_user[:6]=='inner_':                            #if inner then if other user is online send msgs else store them in cache
            if self.room not in cache.get('online',set()):         
                past_msgs=cache.get(self.room)
                if past_msgs==None:past_msgs={}                 
                if data['sender'] in past_msgs:
                    past_msgs[data['sender']].append([data['msg'],get_time_ist()])   
                else:
                    past_msgs[data['sender']]=[[data['msg'],get_time_ist()]]
                cache.set(self.room,past_msgs)                 
            await self.channel_layer.group_send(self.room, {"type": "chat_message" ,"data": data})


    # Receive message from room group
    async def chat_message(self, event):
        data = event["data"]
        if 'online_status' in data:
            pass
        else:
            if 'sent_by' in data:
                data={data['sender']:[[data['msg'],get_time_ist(),data['sent_by']]]}
            else:
                data={data['sender']:[[data['msg'],get_time_ist()]]}      #{sender:[msg1,ts1]}
        # Send message to WebSocket
        await self.send(json.dumps(data))
