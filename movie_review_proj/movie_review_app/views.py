from django.shortcuts import render, redirect
from .models import ContactInfo, Address, User, Movie, Rating
from django.contrib import messages
import bcrypt
import pytz


def time_zone():
    '''Allow the user to select their time  zone.'''
    timezone_list = [(0, 'Select Time Zone')]
    # from pytz timeszones remove the following 
    remove_2 = ['GB', 'NZ']
    remove_3 = ['EET','EST','ETC','GMT','HST','WET',
                'UCT', 'UTC', 'MET','MST','PRC', 'ROC','ROK', 'CET']
    remove_4 = ['W-SU', 'W-SU']
    remove_5 = ['GMT+0', 'GMT-0']
    remove_7 = ['MST7MDT', 'NZ-CHAT', 'GB-Eire', 'PST8PDT', 'EST5EDT', 'CST6CDT']

    idx = 1
    for tz in pytz.all_timezones:
        if tz[0:4] == 'Etc/':
            pass
        elif tz[0:2] in remove_2 and len(tz) == 2:
            pass
        elif tz[0:3] in remove_3 and len(tz) == 3:
            pass
        elif tz[0:4] in remove_4 and len(tz) == 4 :
            pass
        elif tz[0:5] in remove_5 and len(tz) == 5 :
            pass
        elif tz[0:7] in remove_7 and len(tz) == 7:
            pass
        else:
            timezone_list.append((idx,tz))
            idx += 1

    return timezone_list


def convert_tz_idx(request):
    '''This function is used in register_view & profile_view
    It checks the index value of time zone and if 0 it returns 
    value stored in database else converts index to tz name
    Wrap in try/except to catch scenarios when string name is 
    passed e.g., 'America/New_York'
    '''
    try:
        # Time zone stores the assigned index value. Use index value to return string name
        # If user is registering 'active_user_id' is None and will cause error goTo except
        tz_idx = request.POST.get('time-zone-nm', None)
        time_zones = time_zone()
        active_id = request.session['active_user_id']
        
        # get the timezone idx value - returned as string
        if tz_idx == '0':
            # if zero its set to default. Access database and use stored vale
            user = User.objects.get(id=active_id)
            active_tz_idx =  user.timezone
            print(f'Line 60 {active_tz_idx}')
            if active_tz_idx == '0' or active_tz_idx == 'UPDATE TIME ZONE' :
                return 'UPDATE TIME ZONE'
        else:
            # idx number is not zero use value provide
            active_tz_idx = tz_idx
        
        # look up the value based on index. Time_zone returns list of tuples
        for idx, tz in time_zones:
            if tz == active_tz_idx:
                correct_tz_name = tz
                return correct_tz_name
    except:
        # An idx value was provide else it was a name 
        if len(str(tz_idx)) <= 3:
            for idx, tz in time_zones:
                if str(idx) == tz_idx:
                    correct_tz_name = tz 
                    return correct_tz_name
        
        print(f"I am line 85 {request.POST.get('time-zone-nm', None)}") 
        return request.POST.get('time-zone-nm', None)

    

def index_view(request):
    return render(request, 'index.html')


def register_view(request):

    # if POST and User is not logged in they can Register
    if request.method == 'POST':
       
        errors = User.objects.validate_reg(request.POST)
        
        if len(errors) > 0:
            for k, v in errors.items():
                messages.error(request, v)   
            return redirect('/register')
        
        # no errors - salt password and pass to "create"
        password = request.POST.get('reg-password-nm',None)
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        
        # Get user timezone  
        user_tz = convert_tz_idx(request)

        User.objects.create(
            first_name = request.POST.get('reg-first-nm',None),
            last_name = request.POST.get('reg-last-nm',None),
            dob = request.POST.get('reg-dob-nm',None),
            email = request.POST.get('reg-email-nm',None),
            timezone = user_tz,
            picture = 'default-img.jpg',
            password = password_hash,
        )

        # create instance of last record from User 
        user_added = User.objects.all().last()

        ContactInfo.objects.create(
            mobile_phone = request.POST.get('handy-phone-nm',None),
            office_phone =  request.POST.get('office-nm',None),
            office_text =  request.POST.get('office-ext-nm',None),
            url =  request.POST.get('url-nm',None),
            user = user_added,
        )

        Address.objects.create(
            street_number = request.POST.get('street-number-nm',None),
            street_name =  request.POST.get('street-name-nm',None),
            po_box =  request.POST.get('po-box-nm',None),
            state =  request.POST.get('states-nm',None),
            city =  request.POST.get('address-city-nm',None),
            zip_code =  request.POST.get('zip-address-nm',None),
            user = user_added,
        )

        # user created but still not logged in 
        request.session['logged_in'] = False

        return render(request, 'login.html')

    time_zones = time_zone()
    context = {
        'time_zones' : time_zones
    }
    return render(request, 'register.html', context)


def login_view(request):   
    if request.method == 'POST':

        '''if email is not in db then Django returns "IndexError at /login/
        list index out of range". Is there a way to prevent? This will be caught 
        with ValidationManager within models.py but what about before?'''
        errors = User.objects.validation_log(request.POST)
        
        if len(errors) > 0:
            for k, v in errors.items():
                messages.error(request, v)  
            # return JsonResponse(errors, status=200) 
            return redirect('/login')

        active_user = User.objects.filter(email=request.POST.get('log-email-nm', None))
        context = {
            'user' : active_user[0]
        }
        
        # user is logged in 
        request.session['logged_in'] = True
        request.session['active_user_id'] = active_user[0].id
        request.session['active_user_first'] = active_user[0].first_name
        request.session['active_user_last'] = active_user[0].last_name
        # request.session['active_user_picture'] = active_user[0].picture
        # no errors - user logged in
        return render(request, 'index.html', context)


    return render(request, 'login.html')


def profile_view(request):

    if request.method == 'POST':
        # Updating User data skip email. Do not allow user to change
        
        '''is user does not add a profile image. When update selected 
        it will cause an error and cause profile image to be empty'''
        
        active_id = request.session['active_user_id']

        # if no picture attached use picture in database
        picture_name = request.POST.get('user-pic-name-nm',None)
        picture_url = request.POST.get('user-pic-url-nm',None)

        print('********+++++++++************')
        print(f'picture_name {picture_name}')
        print(f'picture_url {picture_url}')
        print('********++++++++++************')

        # user did not update attach any image
        if picture_name == None or picture_name == '':
            # get image name from the database
            user = User.objects.get(id=active_id)
            user_pic_name = user.picture
            profile_pic = request.FILES[user_pic_name]
        else:
            profile_pic = request.FILES[picture_name]

        # create user 
        user_tz = convert_tz_idx(request)
        
        User.objects.update_or_create(
            id=request.session['active_user_id'],
            defaults = {
                'first_name': request.POST.get('user-first-nm',None),
                'last_name': request.POST.get('user-last-nm',None),
                'dob': request.POST.get('user-dob-nm',None),
                'timezone': user_tz,
                # 'email': request.POST.get('user-email-nm',None),
                'display_name': request.POST.get('user-display-nm',None),
                'picture': profile_pic,
                'gender': request.POST.get('user-gender-nm',None),
                'description': request.POST.get('user-desc-nm',None),   
            }
        )

        return redirect('/profile') 
    
    active_id = request.session['active_user_id']
    active_user = User.objects.get(id=active_id)
    # return list of all time zones 
    time_zones = time_zone()

    context = {
        'general' : User.objects.get(id=active_id),
        'user_time_zone': active_user.timezone,
        'contact' : ContactInfo.objects.get(user_id=active_id),
        'address' : Address.objects.get(user_id=active_id),
        'date' : str(User.objects.get(id=active_id).dob),
        'time_zones' : time_zones
    }
    
    user = User.objects.get(id=active_id)
    return render(request, 'user_profile.html', context)


def movie_listing_view(request):
    '''Populate the Movie View page with title, user who added
    and if it was liked or not liked'''

    # On Add Movie page load or redirected to after movie added     
    active_user = User.objects.get(id=request.session['active_user_id'])
    all_movies = Movie.objects.all()
    context = {
        'movies' : all_movies,
        'active_User' : active_user
    }
    return render(request, 'add_movie.html', context)


def add_movie(request):
    '''
    Allow a user that is logged-in to add a new unique movie to the database
    Movie added by user is automatically "LIKED" by user
    Title and Description required with min desc length of 5'''

    if request.method == 'POST' and request.session['logged_in'] == True:
        errors = Movie.objects.validation_added_movie(request.POST)

        if len(errors) > 0:
            for k, v in errors.items():
                messages.error(request, v)   
            return redirect('/movies')

        # Create the User Rating 
        Rating.objects.create(
            rating = request.POST.get('user-movie-rating-nm', None)
        )

        active_user_rating = Rating.objects.last()

        active_user = User.objects.get(id=request.session['active_user_id'])
        movie_added = Movie.objects.create(
            title = request.POST.get('movie-title-nm', None),
            movie_desc = request.POST.get('movie-desc-nm', None),
            movie_rating = active_user_rating,
            user_uploaded = active_user
        )

        movie_added.save()
        movie_added = Movie.objects.last()
        active_user.users_liked.add(movie_added)

        return redirect('/movies')



def edit_movie_view(request, id_movie):
    '''Allow logged in user to edit movie if they added the movie'''

    selected_movie_to_edit = Movie.objects.get(id=id_movie)
    active_user = User.objects.get(id=request.session['active_user_id'])
    
    context = {
        'selected_movie' : selected_movie_to_edit,
        'user_time_zone': active_user.timezone,
    }

    return render(request, 'edit_movie.html', context)


def view_movie_view(request, id_movie):
    '''Allow users to view any movie and add to favorites'''
    return render(request, 'view_movie.html')


def contact_update(request):
    # should always be a POST but add just in-case
    if request.method == 'POST': 

        ContactInfo.objects.filter(user_id=request.session['active_user_id']).update(
            mobile_phone= request.POST.get('handy-phone-nm',None),
            office_phone= request.POST.get('office-nm',None),
            url= request.POST.get('url-nm',None),
            office_text= request.POST.get('office-text-nm',None)
        )

        return redirect('/profile')
    # if not POST but should never happen    
    return render(request, 'user_profile.html')


def profile_update(request):
        # should always be a POST but add just in-case
    if request.method == 'POST': 
        '''PO box is optional. If user does not add make it 0 to prevent 
        and error. '''
        po_box= request.POST.get('po-box-nm',None)
        if po_box == None or po_box == '':
            po_box = 0

        Address.objects.filter(user_id=request.session['active_user_id']).update(
            street_number= request.POST.get('street-number-nm',None),
            street_name= request.POST.get('street-name-nm',None),
            po_box= po_box,
            state= request.POST.get('states-nm',None),
            city= request.POST.get('address-city-nm',None),
            zip_code= request.POST.get('zip-address-nm',None),
        )

        return redirect('/profile')
    # if not POST but should never happen    
    return render(request, 'user_profile.html')


def log_out(request):
        try:
            # log user out
            request.session['logged_in'] = False
            request.session['user_id'] = None

            request.session.flush()
            return render(request, 'index.html')
        except:
            request.session.flush() 
            return redirect('/')     


def delete_movie(request, id_delete):
    '''Allow the active user to delete movie if they added to db'''
    # Create instance if movie to delete 
    movie_to_delete = Movie.objects.get(id=id_delete)
    movie_to_delete.delete()
    return redirect('/add-movie')


def add_like(request, id_like):
    # Create an instance of User which is the logged-in user
    active_user = User.objects.get(id=request.session['active_user_id'])
    # Create an instance of the book
    active_movie = Movie.objects.get(id=id_like)
    # Add active to active book favorites 
    active_movie.user_liked.add(active_user)

    return redirect('/add-movie')


def remove_like(request, id_unlike):
    '''With the book id passed remove this book from active user favorites'''
    # Create an instance of User which is the logged-in user
    active_user = User.objects.get(id=request.session['active_user_id'])
    # Create an instance of the book
    active_movie = Movie.objects.get(id=id_unlike)
    # Add active to active book favorites 
    active_movie.user_liked.delete(active_user)

    return redirect('/add-movie')    


def edit_view_option(request, id_movie):
    '''When User selects the Movie link from the Add Movie
    page they will be directed to the Edit page OR the 
    View Movie Details page. If User uploaded movie they can access 
    edit page else only the details page'''
    active_user_id = request.sessions['active_user_id']

    # Create instance of Movie
    selected_movie = Movie.objects.get(id=id_movie)
    # Get id of user who uploaded 
    uploaded_by_id = selected_movie.user_uploaded.id
    # compare active user id with user who uploaded id
    print(f'Active User id {active_user_id} Uploaded by id: {uploaded_by_id}')

    if int(active_user_id) == (uploaded_by_id):
        # Active user did upload requested movie go to Edit
        edit_url = f'/edit-movie/{id_movie}/'
        return redirect(edit_url)
    
    details_url = f'/view-movie/{id_movie}/'
    return(details_url)