from django.shortcuts import render,redirect
from rest_framework.views import APIView,Response
from rest_framework import permissions,status,generics
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import login,logout
from .serializers import ChangePasswordSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser,FormParser
from datetime import date
from django.core.mail import send_mail
from datetime import datetime,timedelta
import calendar
import re
from urllib.parse import urlencode


# Create your views here.

from twilio.rest import Client
from decouple import config
from django.core.mail import send_mail

# for paymnet handling
import stripe
stripe.api_key = config("STRIPE_SECRET_KEY")
from decouple import config
from django.http import JsonResponse



from .serializers import CreateUserSerializer ,LoginSerializer,EditProfileSerializer,UserAvatarSerializer,PremiumPlanSerializer,AddPremiumSerializer

import json
import requests

from . models import User,OTP,Profile,PremiumPlan
from rent.models import room
import random
from django.contrib.auth.decorators import login_required
from knox.views import LoginView,LogoutView
from knox.auth import TokenAuthentication
from knox.models import AuthToken

@method_decorator(csrf_exempt,name='dispatch')
class SendOTPphone(APIView):
    """
     provide phone  in json format to meet ur request as follow
    {
    "phone" : "8373733743"
   }

    """

    def send_otp(self, phone,otp):

        Account_sid = config('Account_sid')
        auth_token = config('auth_token')
        client = Client(Account_sid, auth_token)
        message = client.messages \
            .create(
            body="Your One Time Password For  DreamHomeRentals.com is {} Please do not share your OTP with Any one ".format(otp),
            to='+91{}'.format(phone),
            from_=config('from'),
        )
        return





    def post(self,request,*args,**kwargs):
        data = request.body
        dict_data = json.loads(data)


        phone_number = dict_data["phone"]

        if phone_number:

            user = User.objects.filter(phone__iexact = phone_number)
            if user.exists():
                return Response({
                    'status': False,
                    'Detail':"Failed to enroll as phone number already taken "
                })
            else:

               key =  SendOTP(phone_number)
               if key:

                   old_otp = OTP.objects.filter(phone = phone_number)
                   if old_otp.exists():
                       old = old_otp.first()
                       count = old.count

                       if count > 4:
                           return Response({
                               'status': False,
                               'Detail': 'OTP sending limit is crossed contact to customer care on 8340312640 '

                           })
                       else:
                           old.count = count+1
                           old.otp = key
                           old.save()
                           self.send_otp(phone_number,key)
                           return Response({
                               "status": True,
                               "OTP": key,
                               "Detail": "OTP sent Successfully "

                           })

                   OTP.objects.create(
                       phone = phone_number,
                       otp = key,
                       count =1
                   )
                   self.send_otp(phone_number, key)
                   return Response({
                       "status": True,
                       "OTP" : key,
                       "Detail": "OTP sent Successfully "


                   })
               else:
                   return Response({
                       'status': False,
                       'Detail': 'Something Went Wrong please contact customer support'

                   })


        else:
            return Response({
                'status': False,
                'Detail': 'Phone Number Not Given plz input valid phone number'

            })


def SendOTP(phone):
    if phone :
        key = random.randint(999,9999)
        print(key)
        return key
    else:
        return False


class validateOTP(APIView):
    """
    if user has already recieved the otp then  redirect to set password for registration
    provide phone and OTP in jason format to meet ur request as follow
    {
    "phone" : "83737337434",
    "otp" : "4848"
    }
    """
    def post(self,request,*args,**kwargs):
        data = request.body
        data_dict = json.loads(data)
        phone = data_dict["phone"]
        sent_otp = data_dict["otp"]
        if phone and sent_otp:
            old = OTP.objects.filter(phone__iexact = phone)
            old = old.first()
            if str(sent_otp) == old.otp :
                old.validated = True
                old.save()
                return Response({
                    "status" : True,
                    "Message " : "OTP Matched proceed for registration "

                })
            else:
                return Response({
                    "status": False,
                    "Message ": "OTP Not Matched Try Again with valid otp "

                })
        else:
            return Response({
                "status": False,
                "Message ": "Enter valid phone number in valid json format "

            })



class Register(APIView):

    """
     provide phone and password in json format to meet ur request as follow
    {

    "phone" : "8737337434",
    "password"   : "Sanjf38339@",
    "email" : "sajjff27636@gmail.com",
    "DOB"   :  "1998-12-30",
    "username" : "sachin"

    }

    """
    def post(self,request,*args,**kwargs):

        data = json.loads(request.body)
        phone = data["phone"]
        password = data["password"]

        if phone and password :
            old = OTP.objects.filter(phone__iexact = phone)
            if old.exists() :
                old = old.first()
                if old.validated:
                    temp_data = {
                        "phone":data['phone'],
                        "password":data['password'],
                        "email" :data['email'],
                        "date_of_birth":data['DOB'],
                        "username":data["username"]

                    }
                    serializer =  CreateUserSerializer(data=temp_data)
                    serializer.is_valid(raise_exception=True)
                    user = serializer.save()
                    old.delete()
                    return Response({
                        "status" : True,
                        "message" : "Account created",
                        "token": AuthToken.objects.create(user)[1]
                    })
                else:
                    return Response({
                        "status": False,
                        "message": "Account not created First verify ur phone"
                    })
            else:

                return Response({
                    "status": False,
                    "message": "Account not created First verify ur phone"
                })
        else:
            return Response({
                "status": False,
                "message": "Enter valid phone or password in json format"
            })



class LoginAPI(LoginView):
    """
     provide phone and password in json format to meet ur login request as follow
    {

    "phone" : "8737337434",
    "password"   : "Sanjf38339@"
    }
    """

    permission_classes = (permissions.AllowAny,)
    def post(self,request, format = None):
        data = request.body
        data = json.loads(data)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request,user)
        res =super().post(request, format=None)

        if user.is_authenticated:
            return Response({
                'status': True,
                'token': res.data['token']
            })


        else:

            return Response({'status' : False})


@method_decorator(login_required, name ="dispatch")
class ChangePasswordView(generics.UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        data = json.loads(request.body)
        serializer = self.get_serializer(data=data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': True,
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@method_decorator(login_required, name ="dispatch")
class EditProfile(APIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = (MultiPartParser,FormParser)

    def put(self, request, format=None):

        data = request.body

        data = json.loads(data)

        queryset = Profile.objects.get(id =data['id'])
        serializer = EditProfileSerializer(queryset,data=data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "UpdatedData":serializer.validated_data,
                'status': True,
                "msg" : "Data successfully updated"

            })
        else:
            return Response({
                "msg": "something went wrong",
                "status": False
            })

def logoutview(request):
    logout(request)
    return redirect('/')

@login_required(login_url='/rent/loginPage')
def ProfileView(request):
    user = Profile.objects.filter(id = request.user.id)

    context = {'data': room.objects.all().filter(user=request.user.profile).order_by("-id"),
               'users': user,
               'rented_house': room.objects.all().filter(Tenant_id=request.user.profile.id).order_by("-id")
               }
    return render(request,'UserProfile.html',context)



def UpdateProfileView(request):
    user = Profile.objects.filter(id = request.user.id)
    date_of_birth = None
    for i in user:
       date_of_birth = i.date_of_birth.strftime("%Y-%m-%d")
    return render(request,'UpdateProfile.html',{'users':user,'date_of_birth':date_of_birth})


# FOR IMAGEFIELD UPLOAD CHECK
@method_decorator(login_required, name ="dispatch")
class UserAvatarUpload(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, format=None):
        user = Profile.objects.get(id = request.data.get('id'))
        serializer = UserAvatarSerializer( instance=user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({

                'status': True,
                "msg": "Data successfully updated"

            })
        else:
            return Response({
                "msg": "something went wrong",
                "status": False
            })



class goToResetPass(APIView):
    def post(self,request, format = None):
        data = request.body

        data = json.loads(data)
        try:

            user = User.objects.filter(email = data['email'])
        except:
            return Response({
                "status":False,
                "msg": "User with this email id is not valid "
            })
        if user.exists():
            BASE_URL = "{0}://{1}/api/".format(request.scheme, request.get_host(), request.path)
            # BASE_URL = "http://127.0.0.1:8000/api/"
            END_POINT = "password_reset/"
            respo = requests.post(BASE_URL + END_POINT, data=data)

            if respo.status_code == 200:

                return Response({

                    "status": True,
                    'msg': 'Reset password link has been sent to your email'
                })
            else:
                return Response({
                    "status": False,
                    "msg": "User with this email id is not valid "
                })




def ConfirmResetPass(request,token):
    print("This cam from email link when you clicked on email link  ",token)

    return render(request,'resetpassword.html',{'token':token})

class ConfirmPassreset(APIView):

    def post(self,request,token, format = None):
        data = request.body
        print("i was called from  confirm Pass Reset")
        data = json.loads(data)

        print(data['password'])
        data['token'] =token
        print(data,"Conform pass se aaya hu SS")

        BASE_URL = "{0}://{1}/api/".format(request.scheme, request.get_host(), request.path)
        # BASE_URL = "http://127.0.0.1:8000/api/"
        END_POINT = "password_reset/confirm/{}".format(token)
        respo = requests.post(BASE_URL + END_POINT, data=data)
        print(respo.json(),"Ye e ConfirmPassreset",respo.status_code)
        if respo.status_code == 200:

            return Response({

                "status": True,
                'msg': 'Password reset successful!'
            })
        else:
            return Response({
                "status": False,
                "msg": respo.json()
            })

class  GetPremiumPlan(APIView):
    def get(self,request, format = None):
        plans =  PremiumPlan.objects.all()
        serializer = PremiumPlanSerializer(plans,many=True)
        return Response(serializer.data)


def ShowPremiumPlan(request):
    plans = PremiumPlan.objects.all()
    if request.method == 'POST' :
        planAdded = request.POST.get("plan")
        plan = PremiumPlan.objects.get(id = planAdded)

        request.user.profile.Premium = True
        request.user.profile.Premium_plan =plan.Amount
        request.user.profile.premium_Validity = plan.Validity
        request.user.profile.premium_start_date = plan.start_date
        request.user.profile.save()
        return redirect('/')



    if request.user.profile.Premium:
        year, month, day = request.user.profile.premium_start_date.split("-")
        start_date = date(int(year), int(month), int(day))
        today = date.today()
        days_left = int(request.user.profile.PremiumDaysLeft) - abs((start_date - today).days)
    
        start_date = request.user.profile.premium_start_date
        months_to_add = int(re.search(r'\d+',request.user.profile.premium_Validity).group())

        date_obj = datetime.strptime(start_date, '%Y-%m-%d')  # Convert string to datetime object
        year = date_obj.year + (date_obj.month + months_to_add - 1) // 12  # Calculate new year
        month = (date_obj.month + months_to_add - 1) % 12 + 1  # Calculate new month
        day = min(date_obj.day, calendar.monthrange(year, month)[1])  # Calculate new day
        new_date_obj = datetime(year, month, day)  # Create new datetime object

        new_date_str = new_date_obj.strftime('%Y-%m-%d')  # Convert the new date object to string format
   
        return render(request,'premiumplan.html',{'plans':plans,'days_left':days_left,'end_date':new_date_str,'start_date':start_date})
    return render(request,'premiumplan.html',{'plans':plans, 'stripe_public_key': config('STRIPE_PUBLIC_KEY')})



class AddPremiumMembership(APIView):
    def get(self, request, format=None):
        data_dic = request.GET.get('data')
        data_json= json.dumps(data_dic)

        data = json.loads(data_json)

        data = json.loads(data)

        plan = PremiumPlan.objects.get(id = data['planId'])
        data['Premium'] = True
        data['Premium_plan'] = plan.Amount
        data['premium_Validity'] = plan.Validity
        data['PremiumDaysLeft'] = int(re.search(r'\d+',plan.Validity).group())*30
        data['premium_start_date'] = data['start_date']
        queryset = Profile.objects.get(id =data['id'])
        serializer = AddPremiumSerializer(queryset,data=data)
        serializer.is_valid(raise_exception=True)
        if serializer.is_valid():
            
            serializer.save()
#           Send message
            Account_sid = config('Account_sid')
            auth_token = config('auth_token')
            client = Client(Account_sid, auth_token)
            message = client.messages \
            .create(
            body=f"""
Dear {data['name']},

    Thank you for choosing Dream Home Rentals. We appreciate your purchase of our {plan.Name} and are excited to assist you in your search for your dream home. Our team is dedicated to providing you with the best possible service and  ensuring that your experience with us is a positive one.

    Please don't hesitate to contact us if you have any questions or concerns regarding your plan. We are always here to help you find the perfect home that meets your needs.

Thank you again for your business.

Best regards,
Dream Home Rentals
            """,
            to='+91{}'.format(data['pno']),
            from_=config('from'),
            )
            
        return redirect("/api/ShowPremiumPlans")

def stripe_checkout(request):
    print("Premium membership")
    data = request.body
    query_params = urlencode({'data': data})
    data = json.loads(data)
    plan = PremiumPlan.objects.get(id = data['planId'])
    price = plan.Amount
    name = f'{plan.Name} ({plan.Validity})'
   
   
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{

            'price_data': {
                'currency': 'INR',
                'product_data': {
                    'name': name,
                    'images': ['https://img.freepik.com/premium-vector/house-real-estate-logo_7169-95.jpg?w=740'],
                },
                'unit_amount': price *100,

            },

            'quantity': 1,
        }],
        mode='payment',
        success_url='http://127.0.0.1:8000/api/AddPremium?'+query_params,
        cancel_url='http://127.0.0.1:8000',
    )
    return JsonResponse({'session_id': session.id})











class ContactUs(APIView):
    def post(self,request,format=None):
        data = request.body
        data = json.loads(data)
        name = data['name']
        email = data['email']
        msg = data['message']
        sub = f"New contact form submission from {name}"
        body = f"Name :{name} \nEmail :{email} \n\n{msg}"


    
        send_mail(sub,body,email,['help.dreamhomerentals@gmail.com'])
        return Response({
            'status': True,
            "msg": "Data successfully updated"

        })
