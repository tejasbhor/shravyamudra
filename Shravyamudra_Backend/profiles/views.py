from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .serializers import ProfileSerializer

class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        data = serializer.data
        data['first_name'] = request.user.first_name
        data['last_name'] = request.user.last_name
        return Response(data)

    def put(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        user = request.user
        # Update user fields if present
        if 'first_name' in request.data:
            user.first_name = request.data['first_name']
        if 'last_name' in request.data:
            user.last_name = request.data['last_name']
        user.save()
        if serializer.is_valid():
            serializer.save()
            data = serializer.data
            data['first_name'] = user.first_name
            data['last_name'] = user.last_name
            return Response(data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        return self.put(request)
