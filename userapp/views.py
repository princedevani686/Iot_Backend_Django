from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import  get_user_model
from .serializers import RegisterSerializers, UserSerializers ,DeviceSerializer ,DeviceDataSerializer
from django.contrib.auth.hashers import check_password
from .models import Device ,DeviceData
from rest_framework.decorators import api_view ,permission_classes
import random
from django.utils.timezone import now ,timedelta ,make_aware ,is_naive
from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string



User = get_user_model()

@api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    if not email:
        return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'error': 'User with this email does not exist'}, status=status.HTTP_404_NOT_FOUND)
  
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    reset_url = f"http://localhost:4200/reset-password/{uidb64}/{token}"

    email_subject = "Password Reset Request"
    email_body = render_to_string('email/reset-password.html', {'reset_url': reset_url, 'user': user})

    send_mail(
        subject=email_subject,
        message="",  
        from_email="devaniprince14@gmail.com",  
        recipient_list=[user.email],
        html_message=email_body,  
    )
    return Response({'message': 'Password reset link sent to email'}, status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid) 
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({'error': 'Invalid reset link'}, status=status.HTTP_400_BAD_REQUEST)

    if not default_token_generator.check_token(user, token):
        return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)

    new_password = request.data.get('password')
    if new_password:
        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
    

class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializers(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                "user": UserSerializers(user).data,
                "message": "Registration successful",
                "access_token": access_token,
                "refresh_token": refresh_token
                
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = User.objects.get(email=email)
            print(f"User found: {user}")
        except User.DoesNotExist:
            return Response({"message": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

        
        if check_password(password, user.password):
            print(f"User authenticated: {user}")
            refresh = RefreshToken.for_user(user)
            return Response({
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "message": "Login successful",
                'user': {  
                    'id': user.id,
                    'username':user.username,
                    'email': user.email
                }
            }, status=status.HTTP_200_OK)
        else:
            print("Authentication failed: Invalid password")
            return Response({"message": "Invalid email or password."}, status=status.HTTP_401_UNAUTHORIZED)

class GetUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        return Response({
            "user": UserSerializers(user).data
        }, status=status.HTTP_200_OK)
    

class DeviceListView(APIView):
    permission_classes = [IsAuthenticated]  
    def get(self, request):
        devices = Device.objects.filter(user=request.user)
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DeviceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)  
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeviceDetailView(APIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request, pk):
        try:
            device = Device.objects.get(pk=pk, user=request.user)
            
        except Device.DoesNotExist:
            return Response({"error": "Device not found or you do not have permission to access it."}, 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = DeviceSerializer(device)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk):
        try:
            device = Device.objects.get(pk=pk, user=request.user)
        except Device.DoesNotExist:
            return Response({"error": "Device not found or you do not have permission to update it."}, 
                            status=status.HTTP_404_NOT_FOUND)

        serializer = DeviceSerializer(device, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            device = Device.objects.get(pk=pk, user=request.user)
            device.delete()
            return Response({"message": "Device deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
    

class DeviceStatusUpdateView(APIView):
    def patch(self, request, pk):
        try:
            device = Device.objects.get(pk=pk)
            device.status = request.data.get('status', device.status)
            device.save()
            
            if device.status == "inactive":
                self.stop_device_simulation(device)
           
            
            return Response({"message": "Device status updated successfully."})
        except Device.DoesNotExist:
            return Response({"error": "Device not found."}, status=status.HTTP_404_NOT_FOUND)
    
    def stop_device_simulation(self, device):
        print(f"Stopping simulation for device {device.id}")
  
class DeviceDataView(APIView):
    def post(self, request):
        device_id = request.data.get('device_id')
        data_type = request.data.get('type')

        if not device_id or not data_type:
            return Response(
                {"error": "Device ID and type are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            device = Device.objects.get(id=device_id)
        except Device.DoesNotExist:
            return Response(
                {"error": "Device not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            value, = self.simulate_data(data_type) 
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        timestamp = now()

        device_data = DeviceData.objects.create(
            device=device,
            type=data_type,
            value=value,
            timestamp=timestamp
        )
        device.last_reading = {
            "value": value,
        }
        device.save()

        serializer = DeviceDataSerializer(device_data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def simulate_data(self, data_type):
        """Simulate data based on the type."""
        if data_type == "temperature":
            value = round(random.uniform(20.0, 30.0), 2)
        elif data_type == "humidity":
            value = round(random.uniform(40.0, 60.0), 2)
        elif data_type == "motion":
            value = random.choice([0, 1])
        else:
            raise ValueError("Unsupported data type")
        
        self.last_simulated_value = value
        return value,


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_devices(request):
    devices = Device.objects.filter(user=request.user)  
    devices_list = [{"id": device.id, "name": device.name ,"type":device.type ,"last_reading":device.last_reading} for device in devices]
    return JsonResponse({"devices": devices_list})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def filter_device_data(request):
    device_id = request.GET.get('device_id')
    time_range = request.GET.get('range', 'daily')  
    if not device_id:
        return JsonResponse({"error": "Missing device_id parameter"}, status=400)

    try:
        device = Device.objects.get(id=device_id, user=request.user)  
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found or unauthorized"}, status=404)

    now_time = now()
    if time_range == 'daily':
        start_date = now_time - timedelta(days=1)
    elif time_range == 'weekly':
        start_date = now_time - timedelta(weeks=1)
    elif time_range == 'monthly':
        start_date = now_time - timedelta(days=30)
    else:
        return JsonResponse({"error": "Invalid time range parameter"}, status=400)

    data = DeviceData.objects.filter(device=device, timestamp__gte=start_date)
    return JsonResponse({'filtered_devices': list(data.values())})


@api_view(['GET'])
@permission_classes([IsAuthenticated])  
def get_chart_data(request):
    device_id = request.GET.get('device_id')
    time_range = request.GET.get('range')

    if not device_id or not time_range:
        return JsonResponse({"error": "Missing device_id or range parameter"}, status=400)

    try:
        device = Device.objects.get(id=device_id, user=request.user)
    except Device.DoesNotExist:
        return JsonResponse({"error": "Device not found or unauthorized"}, status=404)

    # Get the current time
    end_time = now()

    if time_range == 'daily':
        start_time = end_time - timedelta(days=1)
    elif time_range == 'weekly':
        start_time = end_time - timedelta(weeks=1)
    elif time_range == 'monthly':
        start_time = end_time - timedelta(days=30)
    else:
        return JsonResponse({"error": "Invalid range parameter"}, status=400)

    if is_naive(start_time):
        start_time = make_aware(start_time)
    if is_naive(end_time):
        end_time = make_aware(end_time)

    device_data = DeviceData.objects.filter(device=device, timestamp__range=(start_time, end_time))

    data = [{"timestamp": d.timestamp.isoformat(), "value": d.value} for d in device_data]

    return JsonResponse({"device_data": data})








