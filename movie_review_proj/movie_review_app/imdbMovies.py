from bs4 import BeautifulSoup
import requests
from .models import TopMovie


def check_response(resp_obj):
    '''Check if we can connect to site prior to pulling data''' 
    try:
        if resp_obj.status_code == 200:
            print(f"Connection OK: {resp_obj.status_code}")
            return True
    except:
        # If we are not able to access the page what was the HTTP error code
        # 4xx: CLient Server, 5xx: Server Error will be the most common
        print(f"Error: Not 200 return value was: {resp_obj}")
        return False


def make_soup(url):
    '''url is the page to scrape '''
    soup = BeautifulSoup(url.text, 'html.parser')

    '''soup.body will access all of the HTML within the body tags <body>...</body>
    # The table is contained there so no reason to return all of the information within the header, too'''
    body_tag = soup.body

    '''find_all looking for table element with class  and attribute class name chart full-width'''
    table = body_tag.find_all('table',{'class': 'chart full-width'})

    # Check the length of variable table it should contain 1 table
    if len(table) != 1:
        print('Potential ERROR Table length should be equal to 1')

    # table is in the form of result set which is list. convert to bs4 element
    movies = table[0]

    # data resides in 'td' tags
    movie_details = movies.find_all('td')
    return movie_details


def populate_lists(movie_details):
    '''movie_details are all the <td> elements containing the required data. This function
    will return a list of lists '''
    movie_titles = []
    movie_years = []
    IMDb_ratings = []
    images_250 = []

    for i in range(len(movie_details)):
        title = movie_details[i].find('a', href=True, title=True)
        year = movie_details[i].find('span', {'class' : 'secondaryInfo'})
        images = movie_details[i].find('img')

        if movie_details[i].find('img') != None:
            images_250.append(images['src'])

        if movie_details[i].find('strong', title=True) != None:
            IMDb_ratings.append(movie_details[i].find('strong', title=True).text)

        try:
            movie_titles.append(title.text)
            movie_years.append(str(year.text[1:-1]))
        except:
            # if None pass it will throw an error
            pass

    return [images_250, movie_titles, movie_years, IMDb_ratings]


def validate_data(img, title, year, imdb_rate):
    # if the length is not 250 we are missing data
    img = len(img)
    mt = len(title)
    my = len(year)
    rate = len(imdb_rate)
    if mt != 250 or my != 250 or rate != 250 or img != 250:
        print('One or more data points is missing data')
        return False
    return True


def populate_TopMovie():
    '''The four lists of data are in order from highest ranking (1) to lowest (250)
    Populate the TopMovie model with all data'''
    # Convert the address to a raw string 
    url_top_250 = r"https://www.imdb.com/chart/top/"
    page_250 = requests.get(url_top_250)
    
    # If True status  200 
    if check_response(page_250):
        
        # Using requests get address movie_details contains all td elements
        movie_details = make_soup(page_250)

        # data is a list of four lists each with length of 250
        movie_data = populate_lists(movie_details)

        result = validate_data(movie_data[0], movie_data[1],
                               movie_data[2], movie_data[3]
                              )

        # If true all lists had a length of 250
        if result:          
            '''first delete all records in TopMovie db then populate with 
            new top 250 movies. At any given time we only need most recent
            top 250 movies'''

            TopMovie.objects.all().delete()
            
            for idx in range(0,250):
                # add one so rank min val = 1 and max = 250
                TopMovie.objects.create(
                                        rank=idx + 1,
                                        image=movie_data[0][idx],
                                        title=movie_data[1][idx],
                                        release_date=movie_data[2][idx],
                                        rating=movie_data[3][idx]
                                        )
            return True

    return False


    
    