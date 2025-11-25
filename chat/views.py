from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from perplexity import Perplexity
from .models import Conversation, Message
from .serializers import ChatRequestSerializer
import os
from django.conf import settings
from perplexity import Perplexity

# client = Perplexity()
client = Perplexity(api_key=settings.PERPLEXITY_API_KEY)

class ChatAPIView(APIView):
    permission_classes = [IsAuthenticated]  # ✅ ensures user must be logged in

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user_message = serializer.validated_data['message']
        conversation_id = serializer.validated_data.get('conversation_id')
        user = request.user  # ✅ the logged-in user (Admin, Clinic, or Doctor)

        # ✅ Get or create conversation for this user
        if conversation_id:
            try:
                conversation = Conversation.objects.get(id=conversation_id, user=user)
            except Conversation.DoesNotExist:
                return Response({"error": "Conversation not found or not yours"}, status=404)
        else:
            conversation = Conversation.objects.create(user=user)

        # ✅ Save user's message
        Message.objects.create(conversation=conversation, role='user', content=user_message, user=user)

        # ✅ Build message history for Perplexity
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in conversation.messages.all().order_by('created_at')
        ]

        try:
            response = client.chat.completions.create(
                model="sonar",
                messages=history
            )
            assistant_message = response.choices[0].message.content
            sources = getattr(response, "sources", None)

            # ✅ Save assistant reply (no user)
            Message.objects.create(conversation=conversation, role='assistant', content=assistant_message)

            return Response({
                "conversation_id": conversation.id,
                "assistant": assistant_message,
                "sources": sources,
                "user_role": user.role
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
