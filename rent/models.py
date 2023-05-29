from django.db import models
from django.db.models.deletion import CASCADE
# from django.contrib.auth.models import User
from accounts.models import User,Profile
from django.urls import reverse
from django.core.validators import MinValueValidator,MaxValueValidator,RegexValidator
# Create your models here.


class State(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class District(models.Model):
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class City(models.Model):
    dist = models.ForeignKey(District,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
class Locations(models.Model):
    city = models.ForeignKey(City,on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class room(models.Model):
    user = models.ForeignKey(to=Profile, on_delete=CASCADE)
    Owner_Name = models.CharField(max_length=100,null=True)
    Owner_pic = models.ImageField(upload_to='Housepic', null=True, blank=True)
    House_address  =models.TextField(null=False)
    House_video = models.FileField(upload_to='Housevideos/%Y/%m/%d/', null=True,blank=True ,verbose_name="")
    Building_img1 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Room_img1 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Room_img2 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Room_img3 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Landmark = models.TextField(null=False)
    House_Location_link = models.URLField(max_length=200,null= True,blank=True)
    House_Location_map = models.CharField(max_length=800, null=True, blank=True)
    House_type = models.CharField(max_length=100,null = False,default="2BHK/3BHK/SINGLE")
    AllowedFor = models.CharField(max_length=100, null=False, default="All")
    House_description = models.TextField(null = False,default="Write something About how good and what are the facilities your renters will get there like electricity/Water etc")
    Terms_and_conditions = models.TextField(null = False,default="")
    city = models.CharField(max_length=100,null=False)
    state = models.CharField(max_length=100,null=False)
    district = models.CharField(max_length=100,null=False,default="Not Mention")
    location = models.CharField(max_length=100, null=False, default="Not Mention")
    pin_no = models.IntegerField(null=False)
    phone_no = models.CharField(validators=[RegexValidator("^0?[5-9]{1}\d{9}$")], max_length=12)
    Alt_phone_no = models.CharField(validators=[RegexValidator("^0?[5-9]{1}\d{9}$")],default='Not Mention', max_length=12)
    Price = models.IntegerField(null = False, default= 1000)
    Advance = models.IntegerField(null = False, default= 5000)
    date_added = models.DateTimeField(auto_now_add=True)
    Premium = models.BooleanField(default=False)
    Active = models.BooleanField(default=False)
    Status = models.CharField(max_length=100,null=False,default="Rent")
    Tenant_id = models.IntegerField(null = False, default= 0)
    start_date = models.CharField(max_length=20,default="10/10/2000")
    end_date = models.CharField(max_length=20,default="10/10/2000")
    agreement_date = models.CharField(max_length=20,default="10/10/2000")

    def __str__(self):
        return self.Owner_Name

    @property
    def House_imgURL(self):
        try:
            url1 = self.Building_img1.url
        except:
           url1 = ' '
        return url1


class Temporary(models.Model):
    user = models.ForeignKey(to=Profile, on_delete=CASCADE)
    Owner_Name = models.CharField(max_length=100,null=True)
    Owner_pic = models.ImageField(upload_to='Housepic', null=True, blank=True)
    House_address  =models.TextField(null=False)
    House_video = models.FileField(upload_to='Housevideos/%Y/%m/%d/', null=True, verbose_name="")
    Building_img1 = models.ImageField(upload_to='Housepic', null=False, blank=False)
    Room_img1 = models.ImageField(upload_to='Housepic', null=False, blank=False)
    Room_img2 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Room_img3 = models.ImageField(upload_to='Housepic', null=True, blank=True)
    Landmark = models.TextField(null=False)
    House_Location_link = models.URLField(max_length=200,null= True,blank=True)
    House_Location_map = models.CharField(max_length=800, null=True, blank=True)
    House_type = models.CharField(max_length=100,null = False,default="2BHK/3BHK/SINGLE")
    AllowedFor = models.CharField(max_length=100, null=False, default="All")
    House_description = models.TextField(null = False,default="Write something About the facilities your renters will get there like electricity/Water etc")
    Terms_and_conditions = models.TextField(null = False,default="")
    city = models.CharField(max_length=100,null=False)
    state = models.CharField(max_length=100,null=False)
    district = models.CharField(max_length=100, null=False, default="Not Mention")
    location = models.CharField(max_length=100, null=False, default="Not Mention")
    pin_no = models.IntegerField(null=False)
    phone_no = models.CharField(validators=[RegexValidator("^0?[5-9]{1}\d{9}$")], max_length=12)
    Alt_phone_no = models.CharField(validators=[RegexValidator("^0?[5-9]{1}\d{9}$")],default='Not Mention', max_length=12)
    Price = models.IntegerField(null = False, default= 1000)
    Advance = models.IntegerField(null = False, default= 5000)
    Premium = models.BooleanField(default=False)
    


    def __str__(self):
        return self.Owner_Name

    @property
    def House_imgURL(self):
        try:
            url1 = self.Building_img1.url
        except:
           url1 = ' '
        return url1


class Gallerys(models.Model):
    img_name = models.CharField(max_length=200)
    img= models.ImageField(upload_to='Developer_pic')
    des= models.TextField()

    def __str__(self):
        return self.img_name

    @property
    def Gallerys_imgURL(self):
        try:
            url = self.img.url
        except:
            url = ' '
        return url



