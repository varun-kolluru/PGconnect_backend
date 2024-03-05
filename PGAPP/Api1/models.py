from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

class AppUserManager(BaseUserManager):
    def create_user(self,data):
        user = self.model(email=data["email"],username=data["username"],phone=data["phone"],fname=data["fname"],lname=data["lname"])
        user.set_password(data["password"])
        user.save() 
        return user
	
    def create_superuser(self, email, password, username):
        user = self.create_user(email, password , username)
        user.is_superuser = True
        user.save()
        return user


class AppUser(AbstractBaseUser, PermissionsMixin):
	email = models.EmailField(max_length=50, unique=True)
	username = models.CharField(max_length=40,unique=True)
	register_date = models.DateField(auto_now_add=True)
	fname =  models.CharField(max_length=40)
	lname = models.CharField(max_length=40)
	is_active=models.BooleanField(default=True)
	phone=models.CharField(max_length=12)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']
	objects = AppUserManager()

	#def __str__(self):return self.email
	
	@property
	def is_staff(self):
		return self.is_superuser


class Pgs_Data(models.Model):
    class Meta:
          unique_together = (('pgname','username'))
    pgname=models.CharField(max_length=40)
    username=models.ForeignKey(AppUser, on_delete=models.CASCADE, to_field='username')
    floors=models.IntegerField()
    flats=models.IntegerField()
    location=models.CharField(max_length=50)  #str(lat,log)
    address=models.CharField(max_length=100)  
    city=models.CharField(max_length=40)
     
    def __str__(self):return self.pgname
     
class Room_Info(models.Model):
    class Meta:
          unique_together = (('pgid','roomno'))
    roomno=models.IntegerField(default=0)
    pgid=models.IntegerField(default=0)
    capacity=models.IntegerField(default=0)
    
    def __str__(self):return str([self.pgid,self.roomno])
    
class Guest_Info(models.Model):
    class Meta:
          unique_together = (('username','pgid','roomno'))
    roomno=models.IntegerField(default=0)
    pgid=models.IntegerField(default=0)
    username=models.ForeignKey(AppUser, on_delete=models.PROTECT, to_field='username')
    start_date=models.DateTimeField(auto_now_add=True)
    days_stay=models.IntegerField(default=30)
    fee=models.IntegerField(default=0)
    penality=models.IntegerField(default=0)            #penality per unit span

    def __str__(self):return str([self.username,self.pgid,self.roomno])
    
class Payments(models.Model):
    pgid=models.IntegerField(default=0)
    roomno=models.IntegerField(default=0)
    payer=models.CharField(max_length=40)
    name_in_upi=models.CharField(max_length=40)
    method=models.CharField(max_length=30)
    Amount_paid=models.IntegerField(default=0)
    actual_amount=models.IntegerField(default=0)
    payment_date=models.CharField(max_length=20)
    status=models.SmallIntegerField()                  #0=rejected, 1=pending ,2=accepted
    active=models.BooleanField(default=True)
    
    def __str__(self):return str([self.method])