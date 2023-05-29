from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import room, State,District,Locations,Temporary,City,Gallerys
import json
import requests
from accounts.models import Profile,User,PremiumPlan
from django.core.mail import send_mail
from django.views.generic import View
from .mixins import HttpResponseMixin
from.serializers import RoomUploadUSerializer,RoomUpdateUSerializer,RoomMediaFileUpdateSerializer,RoomSerializer
from django.views.generic.edit import UpdateView
# from .forms import roomForm
from django.contrib import messages
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from datetime import date,timedelta,datetime
from urllib.parse import urlencode
import stripe
from decouple import config
from django.http import JsonResponse
from twilio.rest import Client
import pdfkit
from django.template.loader import render_to_string


stripe.api_key = config("STRIPE_SECRET_KEY")

def index(request,section=None):
  
    if request.user.is_authenticated:
      year, month, day = request.user.profile.premium_start_date.split("-")
      start_date = date(int(year), int(month), int(day))
      today = date.today()
      days_left = int(request.user.profile.PremiumDaysLeft) - abs((start_date - today).days)
      if days_left < 0:
         request.user.profile.Premium = False
         request.user.profile.save()
        

    if section:
        return render(request, 'index11.html', {'section': section})

    base_url = "{0}://{1}".format(request.scheme, request.get_host(), request.path)
    print(base_url)
    state = State.objects.all()
    if request.method == 'POST' :

        state_id = request.POST.get("state")
        state = State.objects.get(id=state_id)
        dist_id = request.POST.get("district")
        dist = District.objects.get(id=dist_id)
        city_id = request.POST.get("city")
        city = City.objects.get(id = city_id)
        location_id = request.POST.get("location")
        location = Locations.objects.get(id=location_id)
        AllowedFor = request.POST.get("selectFor")
        House_type = request.POST.get("House_type")

        SearchedObject = room.objects.filter(Q(state__icontains=state.name) and  Q(AllowedFor__icontains=AllowedFor)and Q(House_type__icontains=House_type)and Q(district__icontains= dist.name) and Q(city__icontains= city.name)and Q(location__icontains= location.name))
        search = SearchedObject.filter(Active = True,Premium = True)
        recomend = room.objects.filter(city=city.name)
        recomend = recomend.filter(Active = True,Premium = True)
        if SearchedObject is None:
            messages.info(request, 'No Result Found As of Now')
            return redirect('/')
        return render(request,'SearchResult.html',{'SearchResult':search,'Reco':recomend})
    state = State.objects.all()

    gallery = Gallerys.objects.all()

#    Room = room.objects.filter(Premium = True,Active = True)
    END_POINT = "/rent/GetRoomData"
    respo = requests.get(base_url + END_POINT)

    

    return render(request,'index11.html',{'RoomDetail':respo.json()['results'],'state':state,'gallery':gallery})


# Create your views here.

def loginpage(request):
    Render_to = str(request.GET['next'])
    print(Render_to)

    return render(request,'loginPage.html',{'Render_to':Render_to})


def About(request):
    return render(request,'about.html')

def ContactUs(request):
    return render(request,'contact.html')


def Districts(request):
    state_id = request.GET.get('state')
    # print("selected state is ",state_id)
    dist = District.objects.filter(state_id = state_id).order_by('name')
    return render(request,'load_country.html',{'dists':dist})

def city(request):
    dist_id = request.GET.get('dist')
    # print("selected district is yahi hai ",dist_id)
    dist = City.objects.filter(dist_id = dist_id).order_by('name')
    return render(request,'load_country.html',{'dists':dist})


def locations(request):
    city_id = request.GET.get('city')
    # print("selected city is yahi hai ",city_id)
    dist = Locations.objects.filter(city_id = city_id).order_by('name')
    return render(request,'load_country.html',{'dists':dist})


@login_required(login_url='/rent/loginPage')
def UploadHouseDetail(request):
    if request.user.profile.Premium:

        state = State.objects.all()
        context = {'state':state}
        return render(request, 'FormUpload.html', context)

    else:
        return redirect('/')

@login_required(login_url='/rent/loginPage')
def HouseDetail(request,pk):
    Room = room.objects.filter(id = pk)
    data = list(Room.values())
    list_d = data[0]['House_description'].split(".")
    list_t = data[0]['Terms_and_conditions'].split(".")
    if list_d[-1] == '':
        list_d.remove("")
    if list_t[-1] == '':
        list_t.remove("")
    current_date = date.today()
    today = current_date.strftime("%d/%m/%Y")
    date1 = datetime.strptime(today, '%d/%m/%Y')     
    date2 = datetime.strptime(data[0]['end_date'], '%d/%m/%Y')
    if date1 > date2:
       activate = True
    else:
       activate=False
    return render(request,'property-single.html',{'Detail':Room, 'Desc':list_d, 'Terms':list_t,'stripe_public_key': config('STRIPE_PUBLIC_KEY'),'activate':activate})


@login_required(login_url='/rent/loginPage')
def TenantDetail(request,id):
    pro = Profile.objects.get(id=id)
    
    return render(request,'tenant_detail.html',{'pro':pro})

@login_required(login_url='/rent/loginPage')
def HouseOwnerDetail(request,id):
    pro = Profile.objects.get(id=id)
    
    return render(request,'owner_detail.html',{'pro':pro})







@login_required(login_url='/rent/loginPage')
def AllProperty(request):
    Room = room.objects.all().filter(Premium=True,Active = True)

    return render(request,'property-grid.html',{'rooms':Room})

def PropertyDetail(request):

    return render(request,'property-single.html')

@login_required(login_url='/rent/loginPage')
def ValidationPage(request):
    if request.user.is_admin:
        val = Temporary.objects.all().order_by("-id")
       
        return render(request,'Validate.html',{'Forvalidate':val})
    else:
        return HttpResponse('<h1>Access - Denied </h1>')

@login_required(login_url='/rent/loginPage')
def Validate(request,pk):
    if request.user.is_admin:

        getvalue = Temporary.objects.filter(id = pk)
        for i in getvalue:
            room.objects.create(user=i.user, Owner_Name=i.Owner_Name, House_address=i.House_address, Landmark=i.Landmark,
                                     House_Location_link=i.House_Location_link,House_Location_map=i.House_Location_map,
                                     House_type=i.House_type, House_description=i.House_description, AllowedFor=i.AllowedFor,
                                     state=i.state, city=i.city,location=i.location,Owner_pic=i.Owner_pic,
                                     district=i.district, pin_no=i.pin_no, phone_no=i.phone_no, Building_img1=i.Building_img1,
                                     Room_img1=i.Room_img1,
                                     Room_img2=i.Room_img2, Room_img3=i.Room_img3, House_video=i.House_video,
                                     Alt_phone_no=i.Alt_phone_no, Price=i.Price,Advance=i.Advance,Premium = i.Premium,Active = True).save()

        Temporary.objects.filter(id=pk).delete()
    return HttpResponse("""
    <h1> Validated</h1>
    <button id="button" style="padding="5px 10px"> Go Back</button> 
    <script> 
    document.getElementById('button').addEventListener('click',()=>location.href='http://127.0.0.1:8000/rent/validationpage/')
    </script>
    """)


@login_required(login_url='/rent/loginPage')
def deletePostValidation(request,pk):
    Temporary.objects.filter(id=pk).delete()
    return  HttpResponse("""
    <h1> Deleted </h1>
    <button id="button" style="padding="5px 10px"> Go Back</button> 
    <script> 
    document.getElementById('button').addEventListener('click',()=>location.href='http://127.0.0.1:8000/rent/validationpage/')
    </script>
    """)



@login_required()
def DeletePost(request,pk):
    room.objects.filter(id = pk).delete()
    return render(request,'index11.html')



@login_required(login_url='/rent/loginPage')
def AddPremium(request):

    return render(request,'index11.html')



@login_required(login_url='/rent/loginPage')
def UpdateRooms(request,pk):
    # state = State.objects.all()

    data = room.objects.filter(id = pk)
    obj = room.objects.get(id = pk)

    if request.user.id == obj.user.id:
       return render(request,'UpdatePostRooms.html',{'data': data})
    return HttpResponse("404 BAD REQUEST You Are Not Authorized to Update this Post Invalid Auth Token" )


# API FOR UPLOADING ROOMS

from rest_framework.views import APIView,Response
from rest_framework.parsers import MultiPartParser,FormParser
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework import viewsets,generics



@method_decorator(login_required , name = 'dispatch')
class RoomMediaFileUpdate(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    def partial_update(self, request, pk=None):

        print(" Media file update k liye API CAll hua hai ")
        instance = room.objects.get(id=request.data.get('id'))

        Data =request.data
        print(Data,"Before pop operation")
        for key in list(Data):
            if Data[key]  == 'undefined':
                print(Data[key],"loop k ander se")
                print(Data.pop(key))
        print(Data,"ye delete hone k baad aaya")

        serializer = RoomMediaFileUpdateSerializer(instance=instance, data=Data)
        if serializer.is_valid():
            serializer.save()
            print(serializer.validated_data,"save hone k bad")
            return Response({

                'status': True,
                "msg": "Media File Updated  successfully "

            })
        else:
            print(serializer.validated_data, "save hone k bad")
            return Response({
                "msg": "something went wrong",
                "status": False
            })



@method_decorator(login_required , name = 'dispatch')
class UploadRoomsViewSet(viewsets.ViewSet):

    def list(self, request):
        queryset = room.objects.all(Premium = True,Active = True)
        serializer = RoomSerializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request):
        print(request.data)
        pro = Profile.objects.get(id = int(request.data['user']))
        if pro.Premium:
            request.data['Premium'] =True

        Housemap = request.data['House_Location_map']
        request.data['House_Location_map'] = Housemap[13:271]
 
        request.data['state'] = request.data['state'].lower().title()
        request.data['city'] = request.data['city'].lower().title()
        request.data['location'] = request.data['location'].lower().title()
        request.data['district'] = request.data['district']


        # Get or create city object with foreign key to district
        city_obj, city_created = City.objects.get_or_create(name=request.data['city'], dist=District.objects.get(id=request.data['district']))


        # Get or create town object with foreign key to city
        town_obj, town_created = Locations.objects.get_or_create(name=request.data['location'] , city=city_obj)


        serializer = RoomUploadUSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            send_mail("VALIDATE POST", " Validate This Post  to upload : http://127.0.0.1:8000/rent/validationpage/",
                       'help.dreamhomerentals@gmail.com', ['help.dreamhomerentals@gmail.com'])

            print("Room add ho gya data base me ")
            return Response({

                'status': True,
                "msg": "Data successfully created"

            })
        else:
            return Response({
                'status': False,
                "msg": "something went wrong",

            })

    def partial_update(self, request, pk=None):

        print("Update k liye aa gya hai dekho ")
        queryset = room.objects.get(id=request.data['id'])

        serializer = RoomUpdateUSerializer(queryset, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            print("Room update ho gya hai in database")
            return Response({

                'status': True,
                "msg": "Data successfully updated"

            })
        else:
            return Response({
                'status': False,
                "msg": "something went wrong"+str(serializer.error_messages),

            })

    def destroy(self, request, pk=None):
        pass


class PostActivation(APIView):
    def post(self, request):
        data = request.body
        data = json.loads(data)

        obj = room.objects.get(id=data['id'])
        if data['user_id'] == obj.user.id:
            obj.Active = True
            obj.Status = 'Rent'
            obj.Tenant_id=0
            obj.start_date='01/02/2000'
            obj.end_date='01/02/2000'
            obj.agreement_date='01/02/2000'
            obj.save()
            return Response({
                'status': True,
                'msg': 'Successfully Activated'
            })
        else:
            return Response({
                "status": False,
                "msg": 'Your are not Authorized to update this'
            })


class PostDeactivation(APIView):
    def post(self,request):
        data = request.body
        data = json.loads(data)

        obj = room.objects.get(id=data['id'])
        if data['user_id'] == obj.user.id:
            obj.Active = False
            obj.save()
            return Response({
                'status':True,
                'msg': 'Successfully Deactivated'
            })
        else:
            return Response({
                "status":False,
                "msg": 'Your are not Authorized to update this'
            })

class RoomDataViewSet(generics.ListAPIView):
    queryset = room.objects.filter(Premium=True, Active=True)
    serializer_class = RoomSerializer


def book_succcess(request):
    data_dic = request.GET.get('data')
    data_json= json.dumps(data_dic)
    data = json.loads(data_json)
    data = json.loads(data)
    
    house_id = data['house_id']
    Room = room.objects.get(id=house_id)
    Room.Status = 'Booked'
    Room.Active = False
    Room.Tenant_id = data['tenant_id']
    start = data['start_date']
    start_date = datetime.strptime(start, "%Y-%m-%d").strftime("%d/%m/%Y")  
    Room.start_date = start_date
    end = data['end_date']
    end_date = datetime.strptime(end, "%Y-%m-%d").strftime("%d/%m/%Y")  
    Room.end_date = end_date
    current_date = date.today()
    today = current_date.strftime("%d/%m/%Y")
    Room.agreement_date = today
    Room.save()

    owner_id = data['owner_id']
    profile = Profile.objects.get(id=owner_id)
    owner_name = profile.Fullname
    owner_pho = profile.phone_no
    print(owner_pho)

    today = date.today()
    tomorrow = today + timedelta(days=1)

    
#   Send message to House Owner
    Account_sid = config('Account_sid')
    auth_token = config('auth_token')
    client = Client(Account_sid, auth_token)
    message1 = client.messages \
    .create(
    body=f"""
Dear {owner_name},

We hope this message finds you well. We wanted to inform you that your rental property located at {data['address']} has been booked by a tenant through our platform. The tenant has paid advance payment ₹ {data['advance']}, which has been deposited into your account.

To manage your rental property, you can access your account on our website using this link 🔗️ http://127.0.0.1:8000/api/profile/view/ . We encourage you to keep your account up to date with any changes or updates related to your rental property.

If you have any questions or concerns, please don't hesitate to reach out to us. We are always here to help you.

Thank you for being a part of the Dream Home Rentals community.

Best regards,
Dream Home Rentals

""",
    to='+91{}'.format(owner_pho),
    from_=config('from'),
    )


#   Send message to Tenant
    message2 = client.messages \
    .create(
    body=f"""
Dear {data['tenant_name']},

We are pleased to inform you that your booking for - {data['house_name']} has been confirmed. Your payment of ₹ {data['advance']} has been received and your booking has been approved by the house owner. You can now move in on {tomorrow} and enjoy your new home.

We have also provided a link to manage your booking details and contact the house owner if you have any questions or concerns. Please visit 🔗️ http://127.0.0.1:8000/api/profile/view/

Thank you for choosing Dream Home Rentals. We hope you have a comfortable stay in your new home.

Best regards,
Dream Home Rentals

""",
    to='+91{}'.format(data['tenant_pho']),
    from_=config('from'),
    )



    return redirect("/api/profile/view/")

def stripe_checkout(request):
   
    data = request.body
    query_params = urlencode({'data': data})
    data = json.loads(data)
    price = data['advance']
    name = "Pay Advance"
   
   
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
        success_url='http://127.0.0.1:8000/rent/booking_success?'+query_params,
        cancel_url='http://127.0.0.1:8000',
    )
    return JsonResponse({'session_id': session.id})




def generate_pdf_tenant(request,id):
    pro = Profile.objects.get(id=id)
    pro_img = "http://127.0.0.1:8000"+pro.Profile_pic.url
    no_profile = "http://127.0.0.1:8000/media/Profilepic/blank-profile.png"
    # Render the HTML template with the tenant details
    html = render_to_string('tenant.html', {'pro': pro,'pro_img':pro_img,'no_p':no_profile})

    options = {
    'page-size': 'A4',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm',
    }

    # Generate the PDF from the HTML
    pdf = pdfkit.from_string(html, False,options=options)

    # Send the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="tenant_details.pdf"'
    return response


def generate_pdf_owner(request,id):
    pro = Profile.objects.get(id=id)
    pro_img = "http://127.0.0.1:8000"+pro.Profile_pic.url
    no_profile = "http://127.0.0.1:8000/media/Profilepic/blank-profile.png"
    # Render the HTML template with the tenant details
    html = render_to_string('owner.html', {'pro': pro,'pro_img':pro_img,'no_p':no_profile})

    options = {
    'page-size': 'A4',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm',
    }

    # Generate the PDF from the HTML
    pdf = pdfkit.from_string(html, False,options=options)

    # Send the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="house_owner_details.pdf"'
    return response


def agreement_pdf(request,id):
    Room = room.objects.get(id=id)
    data = Room.Terms_and_conditions
    list_t = data.split(".")
    if list_t[-1] == '':
        list_t.remove("")
   

    tenant = Profile.objects.get(id=Room.Tenant_id)
    owner = Profile.objects.get(id=Room.user_id)

    t_name = tenant.Fullname
    o_name = owner.Fullname
    

    html = render_to_string('agreement.html', {'t_name':t_name, 'o_name':o_name, 'room':Room, 'terms':list_t})

    options = {
    'page-size': 'A4',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm',
    }

    # Generate the PDF from the HTML
    pdf = pdfkit.from_string(html, False,options=options)

    # Send the PDF as a response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="agreement.pdf"'
    return response

































