import json

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache

from datetime import datetime, timedelta


def get_time_ist():
    utc_now = datetime.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)
    return ist_now.strftime("%d-%m %H:%M")

#redis tip for memory management:-  ref:-https://redis.io/docs/reference/eviction/
#set maxmemory parameter, 
#Eviction policies:-allkeys-lru: Keeps most recently used keys; removes least recently used (LRU) keys when memory is full

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room = self.scope["url_route"]["kwargs"]["room_name"]
        await self.channel_layer.group_add(self.room, self.channel_name)
        await self.accept()

        online=cache.get('online_users')
        if online==None:online=set()
        online.add(self.room)
        cache.set('online_users',online)

        chat=cache.get(self.room)
        if chat==None:chat={}
        print(chat)
        await self.send(json.dumps(chat))
        
                                          
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room, self.channel_name)

        online=cache.get('online_users')
        if online!=None and self.room in online:
            online.remove(self.room)
            cache.set('online_users',online)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)   
        data["ts"]=get_time_ist()

        if data["from"][:3]=='PG_':
            grp_mems=set(data.pop("grp_members"))
            for i in grp_mems:
                user_chats=cache.get(i)
                if user_chats==None:
                    user_chats={}
                if data["from"] in user_chats:
                    user_chats[data["from"]].append(data)
                else:
                    user_chats[data["from"]]=[data]
                cache.set(i,user_chats)
                await self.channel_layer.group_send(i, {"type": "chat_message" ,"data": {data["from"]:data}})
        else:
            prev_msgs=cache.get(data["to"])
            if prev_msgs==None:prev_msgs={}
            if data["from"] in prev_msgs:
                prev_msgs[data["from"]].append(data)
            else:
                prev_msgs[data["from"]]=[data]
            cache.set(data["to"],prev_msgs)
            await self.channel_layer.group_send(data["to"], {"type": "chat_message" ,"data": {data["from"]:data}})


    # Receive message from room group
    async def chat_message(self, event):
        data = event["data"]
        await self.send(json.dumps(data))
