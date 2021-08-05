from django.db import models
from django.db.models.deletion import CASCADE
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from datetime import date
import bcrypt

def check_age(born):
    '''Given a birthday calculate the users age based current date.'''
    # Split the string date into y-m-d 
    year, month, day = born.split('-')
    today = date.today()
    return today.year - int(year) - ((today.month, today.day) < (int(month), int(day)))

def unique_email(email):
    user_data = User.objects.all()
    for user in user_data:
        if user.email == email:
            return False
    return True

def check_email(email_str):
    '''Given a string, determine if it is a valid email address
    using Django's validate_email(). Need to do this way. Using 
    validate_email() in validate_reg just returns None'''

    try:
        validate_email(email_str)
        valid_email = True
    except ValidationError:
        valid_email = False

    return valid_email


class ValidationManger(models.Manager):
    def validate_reg(self, post_data):
        errors = {}

        if len(post_data['reg-first-nm']) < 2:
            errors['reg-first-nm'] = 'First name min 2 characters'
        
        if len(post_data['reg-last-nm']) < 2:
            errors['reg-last-nm'] = 'Last name min 2 characters'

        if check_age(post_data['reg-dob-nm']) < 13:
            errors['reg-dob-nm'] = 'Required age is 13 or older'

        # use django val email method 
        if check_email(post_data['reg-email-nm']) == False:
            errors['reg-email-nm'] = 'Email is not valid'

        if not unique_email(post_data['reg-email-nm']):
            errors['reg-email-nm'] = 'This email is already being used'

        if len(post_data['reg-password-nm']) < 8:
            errors['reg-password-nm'] = 'Password should be minimum 8 characters'

        if post_data['reg-password-nm'] != post_data['reg-confirm-nm']:
            errors['reg-password-nm'] = 'Password & confirm password do not match'

        return errors

    def validation_log(self, post_data):
        errors = {}

        # check if email is in the database - returns a list
        user = User.objects.filter(email=post_data['log-email-nm'])
        # if True the email was found in db
        if user:
            logged_user = user[0]
  
            # email is in system - validate pass_wd provided with password in db  
            pass_wd = post_data['log-password-nm']

            if bcrypt.checkpw(pass_wd.encode(),logged_user.password.encode()):
                # password is a match return empty errors
                print(f'NO ERRORS =>>> {errors}')
                return errors
            # password did not match
            errors['log-password-nm'] = 'Password or email is not correct'
            return errors
        # email not in database
        errors['log-email-nm'] = 'Password or email is not correct'
        return errors

    def validation_added_movie(self, post_data):
        errors = {}

        if post_data['movie-title-nm'] == '' or post_data['movie-title-nm'] == None:
            errors['movie-title-nm'] = 'Movie title is required'

        if len(post_data['movie-desc-nm']) < 5 or post_data['movie-desc-nm'] == '':
            errors['movie-desc-nm'] = 'Movie description required with minimum of 5 characters'

        if post_data['user-movie-rating-nm'] == '' or post_data['user-movie-rating-nm'] == None or post_data['user-movie-rating-nm'] == '0': 
            print(f"Result of User Movie Rating: {post_data['user-movie-rating-nm']}")
            errors['user-movie-rating-nm'] = 'Movie rating is required'

        return errors


class User(models.Model):
    first_name = models.CharField(max_length=25, null=False)
    last_name = models.CharField(max_length=25, null=False)
    dob = models.DateField(null=False)
    timezone = models.CharField(max_length=45, default='US/Eastern', null=False)
    email = models.EmailField(max_length=75, unique=True, null=False)
    display_name = models.CharField(max_length=255, null=True)
    # any User instance will have users picture
    picture = models.ImageField(default='default-img.jpg', upload_to='profile_pic',null=True, blank=True)
    gender = models.CharField(max_length=6, null=True)
    description = models.CharField(max_length=255, null=True)
    password= models.CharField(max_length=155,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ValidationManger()
    
    def __str__(self):
        return f'{self.id}, {self.first_name}, {self.last_name}, {self.users_liked}, {self.email}'


class Rating(models.Model):
    rating = models.CharField(max_length=5, default=1, null=False)
    objects = ValidationManger()

    def __str__(self):
        return f'{self.id}, {self.rating}'

class Movie(models.Model):
    title = models.CharField(max_length=50, null=False)
    movie_desc = models.CharField(max_length=255, null=True)
    movie_rating = models.ForeignKey(Rating, related_name="movie_ratings", on_delete=models.CASCADE)
    user_uploaded = models.ForeignKey(User, related_name="users_uploaded",on_delete=models.CASCADE)
    user_liked = models.ManyToManyField(User, related_name="users_liked")
    objects = ValidationManger()

    def __str__(self):
        return f'{self.id}, {self.title}, {self.user_liked}, {self.user_uploaded.email}'  


class ContactInfo(models.Model):
    mobile_phone = models.CharField(max_length=12, null=True, unique=True)
    office_phone = models.CharField(max_length=12, null=True, unique=False)
    office_text = models.CharField(max_length=10, null=True)
    url = models.URLField(max_length=200, unique=False, null=True)
    user = models.OneToOneField(User, related_name='user_contact', on_delete=models.CASCADE, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'Cont. ID => {self.user}, User ID => {self.user}, {self.url}'

class Address(models.Model):
    street_number = models.IntegerField(null=True)
    street_name = models.CharField(max_length=100, null=True)
    po_box = models.IntegerField(null=True)
    state = models.CharField(max_length=50, null=True)
    city = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=15, null=True)
    user = models.OneToOneField(User, related_name='user_address', on_delete=models.CASCADE, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f'User ID => {self.user}, {self.user.first_name}, | {self.city}'