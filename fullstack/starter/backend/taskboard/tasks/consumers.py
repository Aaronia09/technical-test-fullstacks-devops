from channels.generic.websocket import AsyncJsonWebsocketConsumer

class TasksConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.channel_layer.group_add("tasks", self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("tasks", self.channel_name)

    async def task_update(self, event):
        # event['data'] contains the payload we pushed
        await self.send_json(event["data"])
