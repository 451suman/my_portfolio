import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import ChatRoom, ChatMessage, Notification, OnlineUser

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat functionality
    """
    
    async def connect(self):
        self.room_slug = self.scope['url_route']['kwargs']['room_slug']
        self.room_group_name = f'chat_{self.room_slug}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Mark user as online
        if self.scope['user'].is_authenticated:
            await self.mark_user_online(self.scope['user'])
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Mark user as offline
        if self.scope['user'].is_authenticated:
            await self.mark_user_offline(self.scope['user'])
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'text')
        
        if message_type == 'text':
            await self.handle_text_message(data)
        elif message_type == 'typing':
            await self.handle_typing_indicator(data)
        elif message_type == 'reaction':
            await self.handle_reaction(data)
    
    async def handle_text_message(self, data):
        if not self.scope['user'].is_authenticated:
            await self.send_error('Authentication required')
            return
        
        try:
            # Save message to database
            message = await self.save_message(
                content=data['content'],
                message_type='text'
            )
            
            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': message.id,
                        'content': message.content,
                        'author': message.author.username,
                        'author_id': message.author.id,
                        'created_at': message.created_at.isoformat(),
                        'message_type': message.message_type,
                        'is_edited': message.is_edited,
                    }
                }
            )
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_typing_indicator(self, data):
        if not self.scope['user'].is_authenticated:
            return
        
        # Broadcast typing indicator to room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user': self.scope['user'].username,
                'is_typing': data.get('is_typing', False)
            }
        )
    
    async def handle_reaction(self, data):
        if not self.scope['user'].is_authenticated:
            await self.send_error('Authentication required')
            return
        
        try:
            message_id = data['message_id']
            emoji = data['emoji']
            
            # Add reaction to message
            await self.add_reaction(message_id, emoji, self.scope['user'])
            
            # Broadcast reaction update
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'reaction_update',
                    'message_id': message_id,
                    'emoji': emoji,
                    'user': self.scope['user'].username
                }
            )
        except Exception as e:
            await self.send_error(str(e))
    
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def typing_indicator(self, event):
        # Send typing indicator to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': event['user'],
            'is_typing': event['is_typing']
        }))
    
    async def reaction_update(self, event):
        # Send reaction update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'message_id': event['message_id'],
            'emoji': event['emoji'],
            'user': event['user']
        }))
    
    async def send_error(self, error_message):
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': error_message
        }))
    
    @database_sync_to_async
    def save_message(self, content, message_type):
        room = ChatRoom.objects.get(slug=self.room_slug)
        message = ChatMessage.objects.create(
            room=room,
            author=self.scope['user'],
            content=content,
            message_type=message_type
        )
        
        # Update room last activity
        room.last_activity = timezone.now()
        room.save()
        
        return message
    
    @database_sync_to_async
    def add_reaction(self, message_id, emoji, user):
        message = ChatMessage.objects.get(id=message_id)
        message.add_reaction(user, emoji)
    
    @database_sync_to_async
    def mark_user_online(self, user):
        OnlineUser.mark_online(user, self.channel_name)
    
    @database_sync_to_async
    def mark_user_offline(self, user):
        OnlineUser.mark_offline(user)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications
    """
    
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        
        self.user_group_name = f'notifications_{self.scope["user"].id}'
        
        # Join notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Mark user as online
        await self.mark_user_online(self.scope['user'])
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave notification group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        
        # Mark user as offline
        if self.scope['user'].is_authenticated:
            await self.mark_user_offline(self.scope['user'])
    
    async def send_notification(self, event):
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    @database_sync_to_async
    def mark_user_online(self, user):
        OnlineUser.mark_online(user, self.channel_name)
    
    @database_sync_to_async
    def mark_user_offline(self, user):
        OnlineUser.mark_offline(user)


class OnlineUsersConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for tracking online users
    """
    
    async def connect(self):
        if not self.scope['user'].is_authenticated:
            await self.close()
            return
        
        # Join online users group
        await self.channel_layer.group_add(
            'online_users',
            self.channel_name
        )
        
        # Mark user as online
        await self.mark_user_online(self.scope['user'])
        
        # Send current online users list
        await self.send_online_users_list()
        
        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave online users group
        await self.channel_layer.group_discard(
            'online_users',
            self.channel_name
        )
        
        # Mark user as offline
        if self.scope['user'].is_authenticated:
            await self.mark_user_offline(self.scope['user'])
    
    async def user_status_update(self, event):
        # Send user status update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user': event['user'],
            'status': event['status']
        }))
    
    async def send_online_users_list(self):
        online_users = await self.get_online_users()
        await self.send(text_data=json.dumps({
            'type': 'online_users',
            'users': online_users
        }))
    
    @database_sync_to_async
    def mark_user_online(self, user):
        OnlineUser.mark_online(user, self.channel_name)
    
    @database_sync_to_async
    def mark_user_offline(self, user):
        OnlineUser.mark_offline(user)
    
    @database_sync_to_async
    def get_online_users(self):
        online_users = OnlineUser.get_online_users()
        return [
            {
                'username': online_user.user.username,
                'id': online_user.user.id,
                'last_seen': online_user.last_seen.isoformat()
            }
            for online_user in online_users
        ]
