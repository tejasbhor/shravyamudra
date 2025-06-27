from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from .models import UserAPIKey
from .serializers import UserAPIKeySerializer, UserAPIKeySetSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from .gemini_api import call_gemini_api
from .ollama_api import call_ollama_api

class GeminiAPIKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_api_key = UserAPIKey.objects.get(user=request.user)
            return Response({'has_key': bool(user_api_key.gemini_api_key)})
        except UserAPIKey.DoesNotExist:
            return Response({'has_key': False})

    def post(self, request):
        api_key = request.data.get('api_key')
        if not api_key:
            return Response({'error': 'API key is required'}, status=400)

        user_api_key, _ = UserAPIKey.objects.get_or_create(user=request.user)
        user_api_key.gemini_api_key = api_key
        user_api_key.save()
        return Response({'success': True})

    def delete(self, request):
        try:
            user_api_key = UserAPIKey.objects.get(user=request.user)
            user_api_key.gemini_api_key = ''
            user_api_key.save()
            return Response({'success': True})
        except UserAPIKey.DoesNotExist:
            return Response({'success': True})  # Already doesn't exist

class TranslationAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        text = data.get('text', '').strip()
        model = data.get('model', 'local')
        api_key = data.get('apiKey')
        options = data.get('options', {})

        if not text:
            return Response({'success': False, 'error': 'No text provided.'}, status=400)

        try:
            if model == 'gemini-pro':
                # Use provided api_key, else fetch from user
                if not api_key:
                    try:
                        user_api_key = UserAPIKey.objects.get(user=request.user)
                        api_key = user_api_key.gemini_api_key
                    except UserAPIKey.DoesNotExist:
                        return Response({'success': False, 'error': 'No Gemini API key found for user.'}, status=403)
                converted = call_gemini_api(api_key, text)
            elif model == 'local':
                # Use Ollama for local model
                ollama_model = options.get('ollama_model', 'mistral')
                try:
                    converted = call_ollama_api(text, model_name=ollama_model)
                except Exception as e:
                    if "Could not connect to Ollama" in str(e):
                        return Response({
                            'success': False,
                            'error': 'Local LLM service is not running. Please start Ollama or try using Gemini Pro.'
                        }, status=503)
                    raise e
            else:
                return Response({'success': False, 'error': f'Invalid model: {model}'}, status=400)

            return Response({'success': True, 'convertedText': converted})
            
        except Exception as e:
            logging.exception("Translation failed")
            error_msg = str(e)
            if model == 'local':
                error_msg = f"Local LLM translation failed: {error_msg}"
            else:
                error_msg = f"Gemini API translation failed: {error_msg}"
            return Response({'success': False, 'error': error_msg}, status=500)

