from bs4 import BeautifulSoup as bs
from math import floor
from PIL import Image
import customtkinter as ctk
import threading
import subprocess
import webbrowser
import tmdbsimple as tmdb
import requests
import json
import os
import re

#
# API Key Page Modules
#

def write_api_data( self, cipher_suite, api_data ):
    with open( "./data/api_data.txt", 'wb' ) as wf:
        tmp = api_data[0] + '#' + api_data[1] + '#' + api_data[2] + '#' + api_data[3]
        wf.write( cipher_suite.encrypt(tmp.encode('utf-8')) )

def to_browser():
    webbrowser.open("https://www.themoviedb.org/settings/api")

def test_api_key( self, api_key ):
    # Try to login to TMDB
    response = requests.get( url=('https://api.themoviedb.org/3/movie/11?api_key='+api_key) )

    # Return key if login is successful
    if( response.status_code == 200 ):
        return api_key
    else:
        return False

def api_key_submit( self ):
    # Test user-entered key
    api_key = test_api_key( self, self.entrybox.get() )
    # If successful, write to file and show next button
    if ( api_key ):
        # Write to file
        self.controller.api_data[0] = api_key
        write_api_data( self, self.controller.cipher_suite, self.controller.api_data )
        # Add LABEL for SUCCESSMSG
        self.login_state.configure( text="Logged in successfully!" )
        self.login_state.grid( row=2, column=0, columnspan=2, padx=20, pady=10, sticky="new" )
        # Enable 'Next' BUTTON
        self.controller.next_button.configure(state="normal")
        self.controller.next_frame = "MediaSearchPage"
    else:
        # Add LABEL for ERRORMSG
        self.login_state.configure( text="Login unsuccessful, please try again..." )
        self.login_state.grid( row=2, column=0, columnspan=2, padx=20, pady=10, sticky="new" )
        # Disable 'Next' BUTTON
        self.controller.next_button.configure(state="disabled")
    
#
#
#

#
# Media Search Page Modules
#
def select_directory( self ):
    self.controller.folderpath = ctk.filedialog.askdirectory()
    self.folder_path_entry.delete(0)
    self.folder_path_entry.insert(0, self.controller.folderpath)
    if( self.controller.frames['FileMatchPage'].submenu_selection_id != -1 ):
        self.controller.next_button.configure(state="normal")
        self.controller.next_frame = "FileMatchPage"

def search_for_entry( self, search_term ):
    url = 'https://www.dvdcompare.net/comparisons/search.php'
    payload = {
        'param': search_term,
        'searchtype': 'text'
    }

    try:
        response = requests.post( url=url, data=payload, timeout=(30, None) )
    except:
        # need to create an if/else for when it can't connect to dvdcompare
        print(f"An error occurred...") # response code 200 is the only one we want
        self.name_button.configure( state='normal' )
        return

    self.html_doc = bs(response.content, 'html.parser')
    self.content = (self.html_doc.body.find('ul', style="list-style-type:none;padding:0;margin-left:0")).find_all('a')

    self.results_names.clear()
    for item in self.content:
        self.results_names.append( rms(item.string) )
    
    self.name_button.configure( state='normal' )
    populate_sframe( self )

def rms(text):
  # Replaces multiple spaces with a single space in a string.
  return re.sub(r"\s+", " ", text)

def populate_sframe( self ):
    # delete old buttons from frame
    if ( len(self.sframe_buttons) ):
        for button in self.sframe_buttons:
            button.destroy()
        self.sframe_buttons.clear()
    
    # add new buttons to frame
    for i, value in enumerate( self.results_names ):
            button = ctk.CTkButton( self.sframe, text=value, command=lambda id=i, name=value:sframe_submenu(self, id, name) )
            button.grid( row=i, column=0, padx=5, pady=(5,5), sticky="ew" )
            self.sframe_buttons.append( button )

def sframe_submenu( self, entry_index, name ):
        # set (or reset) movie name and submenu index
        disc_type_regex = re.compile(r'Blu-ray|Blu-ray 4K|HD DVD')
        result = disc_type_regex.search( name )
        if( result != None ):
            self.controller.disc_type = result.group().replace('-', '')
        else:
            self.controller.disc_type = 'DVD'
        self.controller.movie_name = ((name.replace("(Blu-ray) ", '')).replace("(Blu-ray 4K) ", '')).replace("(HD DVD) ", '')
        self.controller.frames['FileMatchPage'].submenu_selection_id = -1
        
        # checking for old entries
        if ( len(self.sub_sframe_buttons) ):
            for button in self.sub_sframe_buttons:
                button.destroy()
            self.sub_sframe_buttons.clear()

        # adding back button
        button = ctk.CTkButton( self.sub_sframe, text="back", command=lambda:top_menu(self) )
        button.grid( row=0, column=0, padx=5, pady=(10,0), sticky="ew" )
        self.sub_sframe_buttons.append( button )

        # retrieving movie versions
        self.results_versions.clear()
        search_for_entry_version( self, entry_index )

        # adding movie versions to subframe
        for i, value in enumerate( self.results_versions, start=1 ):
            button = ctk.CTkButton( self.sub_sframe, text=value, command=lambda id=i:submenu_selection(self, id-1) )
            button.grid( row=i, column=0, padx=5, pady=(10,0), sticky="ew" )
            self.sub_sframe_buttons.append( button )
        
        self.sub_sframe.grid( row=2, column=0, columnspan=2, padx=0, pady=0, sticky="nsew" )
        self.sub_sframe.grid_columnconfigure( index=0, weight=1 )
        self.sub_sframe.tkraise()
    
def top_menu( self ):
    self.sub_sframe.grid_forget()

def search_for_entry_version( self, entry_index ):

    selection = self.content[entry_index]['href'].replace('film.php?fid=', '')

    url = "https://www.dvdcompare.net/comparisons/film.php?fid=" + selection
    self.html_doc = bs(requests.get(url).content, 'html.parser')

    self.html_doc = ((self.html_doc.find('div', id='content')).find('table')).find_all('ul')

    for i, item in enumerate(self.html_doc):
        self.results_versions.append( item.li.find('h3').a.get_text(strip=True) )

def submenu_selection( self, id ):
    # save the ID
    self.controller.frames['FileMatchPage'].submenu_selection_id = id
    # Enable 'Next' button
    if( len(self.folder_path_entry.get()) != 0 ):
        self.controller.next_button.configure(state="normal")
        self.controller.next_frame = "FileMatchPage"
#
#
#

#
# File Match Page Modules
#
def match_files( self ):
    
    # read files in folderpath from MediaSearchPage
    contents = os.listdir( self.controller.folderpath )
    container_types = re.compile( r'\.mkv|\.mp4|\.mov|\.avi' )
    for item in contents:
        file_type = container_types.search(item)
        if ( file_type ):
            try:
                duration = get_duration( self.controller.folderpath+'/'+item )
                self.controller.files.append([duration, self.controller.folderpath+'/'+item, file_type.group()])
            except:
                print("An Error Occurred")
    
    # get extras for selected disc
    html_doc = self.controller.frames['MediaSearchPage'].html_doc[self.submenu_selection_id]
    lists = html_doc.find_all('li')
    metadata = {}
    for list in lists:
        if ( list.div ):
            data = list.find('div', class_="description").get_text(separator='%', strip=True).split('%')
            metadata[list.find('div', class_="label").get_text(strip=True)] = data
    for item in metadata['Extras:']:
        # string cleaning
        # timecode regex minutes, string number, and possible dash
        num_timecode_regex = re.compile(r'(\d)+:\d\d|(\d)+:\d\d:\d\d')
        str_timecode_regex = re.compile(r'(\s)*\(.*(\d)+:\d\d\)|(\s)*\(.*(\d)+:\d\d:\d\d\)')
        dash_regex = re.compile(r'(\s)*-(\s)+|(\s)+-(\s)*')

        test = num_timecode_regex.search(item)
        test2 = str_timecode_regex.search(item)
        test3 = dash_regex.search(item)

        if ( test and test2 ):
            name = item.replace(test2.group(), "")
            name = name.replace('\"', "")
            name = name.replace(':', "")
            name = name.replace('\'', "")
            name = name.replace('/', " and ")
            name = name.replace('â', "")
            
            if ( test3 ):
                name = name.replace(test3.group(), "")
            extra_type = findExtraType( name )
            runtime = timecode_to_seconds( str(test.group()) )
            self.controller.extras.append( [runtime, name, extra_type] )

    # rename main feature
    ## TMDB object setup
    tmdb.API_KEY = self.controller.tmdb_api_key
    ## prepping movie title
    year_regex = re.compile(r'\d\d\d\d')
    self.controller.movie_name = self.controller.movie_name.replace(':', '')
    movie_name = self.controller.movie_name
    movie_year = year_regex.search( movie_name ).group()
    movie_name = (movie_name.replace( movie_year, '' )).replace(" ()", '')
    if( movie_name.find(" AKA ") ):
        movie_names = movie_name.split( " AKA " )
    ## search tmdb for movies, test runtime against unmatched files
    match_found = False
    for name in movie_names:
        response = tmdb.Search().movie(query=name, year=int(movie_year))
        print( name )
        for entry in response['results']:
            print( entry )
            for file in self.unmatched_files:
                #print (tmdb.Movies(entry['id']).info()['runtime'] * 60)
                #print (unmatched_files[0][0])
                # NEED TO PLAY WITH RUNTIME DELTA
                # CURRENT DELTA: 60s
                print( str(tmdb.Movies(entry['id']).info()['runtime'] * 60) + " " + str(self.unmatched_files[file][0]) )
                if( -90 < (tmdb.Movies(entry['id']).info()['runtime'] * 60 - self.unmatched_files[file][0]) and
                (tmdb.Movies(entry['id']).info()['runtime'] * 60 - self.unmatched_files[file][0]) < 90 ):
                    self.dest_dir = self.controller.folderpath + '/' + name + f" ({movie_year})"
                    print(self.dest_dir)
                    self.controller.tmdb_id = entry['id']
                    try:
                        os.rename( self.unmatched_files[file][1], self.dest_dir + '/' + self.controller.movie_name + " - " + self.controller.disc_type + self.unmatched_files[file][2] )
                        match_found = True
                    except FileExistsError:
                        print( "File already exists..." )
                    self.unmatched_files[file][1] = self.dest_dir + '/' + self.controller.movie_name + " - " + self.controller.disc_type + self.unmatched_files[file][2]
                    self.matched_files[file] = self.unmatched_files[file]
                    del self.unmatched_files[file]
                    break
            break
        if( match_found ):
            break

    # create new folder in current directory
    try:
        os.mkdir( self.dest_dir )
    except FileExistsError:
        print ( f'{self.dest_dir} already exists...' )
    except FileNotFoundError:
        print ( f'{self.dest_dir} not found...' )

    # match extras
    counter = 0
    self.matched_files = {}
    self.unmatched_files = {}
    for file in self.controller.files:
        self.unmatched_files[counter] = file
        counter += 1
    self.unmatched_extras = {}
    for extra in self.controller.extras:
        self.unmatched_extras[counter] = extra
        counter += 1

    index_to_delete = []
    for extra in self.unmatched_extras:
        for i, file in enumerate( self.controller.files ):
            if ( -0.5 < (self.unmatched_extras[extra][0]-file[0]) and (self.unmatched_extras[extra][0]-file[0]) < 0.5 ):
                try:
                    os.rename( file[1], self.dest_dir + '/' + self.unmatched_extras[extra][1] + self.unmatched_extras[extra][2] + file[2] )
                except FileExistsError:
                    print( f"File {self.unmatched_extras[extra][1]} already exists")
                file[1] = self.dest_dir + '/' + self.unmatched_extras[extra][1] + self.unmatched_extras[extra][2] + file[2]
                self.matched_files[i] = file
                del self.unmatched_files[i]
                index_to_delete.append(extra)

    for key in index_to_delete:
        del self.unmatched_extras[key]

    # populate matched/unmatched lists
    populate_frames( self )

# A function to decipher what kind of extra a video file is
def findExtraType( name ):
  name = name.lower()
  extra_type = name.find("featurette")
  if ( extra_type != -1 ):
    return "-featurette"
  extra_type = name.find("interview")
  if ( extra_type != -1 ):
    return "-interview"
  extra_type = name.find("extended")
  if ( extra_type != -1 ):
    return "-scene"
  extra_type = name.find("trailer")
  if ( extra_type != -1 ):
    return "-trailer"
  extra_type = name.find("deleted")
  if ( extra_type != -1 ):
    return "-deleted"
  return "-other"

def timecode_to_seconds( timecode ):
  split_str = timecode.split(':')
  return ( float(split_str[0]) * 60 + float(split_str[1]) )

def get_duration( file_path ):
    stdout_data, stderr_data = subprocess.Popen( ['./bin/HandBrakeCLI.exe', '-i', file_path, '--scan', '--json'],
                                                stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True ).communicate()
    file_data = json.loads( stdout_data.split( 'JSON Title Set: ' )[1].replace("'", "\"") )
    seconds = ( file_data['TitleList'][0]['Duration']['Hours']*60*60 +
                file_data['TitleList'][0]['Duration']['Minutes']*60 + file_data['TitleList'][0]['Duration']['Seconds'] )
    return seconds

def populate_frames( self ):
    
    """# add new buttons to frame
    for i, value in enumerate( matched ):
            label = ctk.CTkLabel( self.matched_files, text=value[1].replace(self.controller.folderpath, ''),
                                  anchor='w', fg_color='green', corner_radius=4 )
            label.grid( row=i, column=0, padx=2, pady=2, sticky="ew" )
            self.matched_labels.append( label )
    for i, value in enumerate( unmatched ):
            label = ctk.CTkButton( self.unmatched_files, text=value[1].replace(self.controller.folderpath, ''),
                                  anchor='w', fg_color='red', corner_radius=4, command=self.show_unmatch_submenu )
            label.grid( row=i, column=0, padx=2, pady=2, sticky="ew" )
            self.unmatched_labels.append( label )"""
    
    # add new buttons to frame
    for i in self.matched_files:
        value = self.matched_files[i]
        label = ctk.CTkLabel( self.matched_frame, text=value[1].replace(self.controller.folderpath, ''),
                            anchor='w', fg_color='green', corner_radius=4 )
        label.grid( row=i, column=0, padx=2, pady=2, sticky="ew" )
        self.matched_labels[i] = label
    for i in self.unmatched_files:
        value = self.unmatched_files[i]
        label = ctk.CTkButton( self.unmatched_frame, text=(str(value[0]) + " " + value[1].replace(self.controller.folderpath, '')),
                            anchor='w', fg_color='red', corner_radius=4, command=lambda id=i:unmatched_subframe( self, id )  )
        label.grid( row=i, column=0, padx=2, pady=2, sticky="ew" )
        self.unmatched_labels[i] = label

    # Prep images, then enable 'Next' button
    new_thread = threading.Thread( target=lambda:get_images(self.controller.frames['PosterSelectPage']) )
    new_thread.start()

def unmatched_subframe( self, unmatched_id ):
        # adding back button
        button = ctk.CTkButton( self.unmatched_extras_frame, text="back", command=lambda:self.unmatched_extras_frame.grid_forget() )
        button.grid( row=0, column=0, padx=5, pady=(10,0), sticky="ew" )
        self.extras_labels['back'] = button

        # adding extras to subframe
        for i in self.unmatched_extras:
            value = self.unmatched_extras[i]
            button = ctk.CTkButton( self.unmatched_extras_frame, text=value, command=lambda id=i,value=value:manual_match(self, unmatched_id, id, value) )
            button.grid( row=i+1, column=0, padx=5, pady=(10,0), sticky="ew" )
            self.extras_labels[i] = button

        self.unmatched_extras_frame.grid( row=1, column=1, padx=(5,0), pady=(0,10), sticky="nsew" )
        self.unmatched_extras_frame.tkraise()
    
def manual_match( self, unmatched_id, id, value ):        
        # rename files
        os.rename( self.unmatched_files[unmatched_id][1], self.dest_dir + '/' + self.unmatched_extras[id][1] + self.unmatched_extras[id][2] + self.unmatched_files[unmatched_id][2] )
        # add to matched list and labels
        self.matched_files[unmatched_id] = self.unmatched_files[unmatched_id]
        new_label = ctk.CTkLabel( self.matched_frame, text=value[1], anchor='w', fg_color='green', corner_radius=4  )
        new_label.grid( column=0, padx=2, pady=2, sticky="ew"  )
        self.matched_labels[unmatched_id] = new_label
        # remove from unmatched list and labels
        del self.unmatched_files[unmatched_id]
        self.unmatched_labels[unmatched_id].grid_forget()
        del self.unmatched_labels[unmatched_id]
        # go back to top menu
        match_top_menu( self )
        # remove from unmatched extras
        self.extras_labels[id].grid_forget()
        del self.extras_labels[id]
        del self.unmatched_extras[id]

def match_top_menu( self ):
    self.unmatched_extras_frame.grid_forget()
    
#
#
#

#
# PosterSelectPage Modules
#

def get_images( self ):
    images = []
    response = tmdb.Movies(self.controller.tmdb_id).images(language='en')
    for poster in response['posters']:
        images.append('https://images.tmdb.org/t/p/w500'+poster['file_path'])
    
    for i, image in enumerate(images):
        my_image = ctk.CTkImage(light_image=Image.open(requests.get(url=image, stream=True).raw),
                                size=(160, 240))
        image_label = ctk.CTkButton(self.my_sframe, image=my_image, command=lambda url=image:download_file(self, url),
                                    text="", border_spacing=10, fg_color="transparent")  # display image with a CTkLabel
        image_label.grid( row=(i - (i%4)), column=(i%4), padx=(5,0), pady=(5,0), sticky="nsew" )
        self.image_labels.append( image_label )
    self.my_sframe.grid( row=1, column=0, padx=10, pady=10, sticky="nsew")
    self.download_confirm_label.grid( row=2, column=0, padx=0, pady=0, sticky="nsew" )
    self.controller.next_button.configure(state="normal")
    self.controller.next_frame = "PosterSelectPage"

def download_file(self, url):
    self.download_confirm_label.configure( text="" )
    url = url.replace( "w500", "original" )
    download_path = self.controller.folderpath + '/' + self.controller.movie_name + '/poster.jpg'
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True) # Use stream=True for large files

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Open the local file in binary write mode
        with open(download_path, 'wb') as file:
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)
        self.download_confirm_label.configure( text=f"File downloaded successfully to: {download_path}" )

    except requests.exceptions.RequestException as e:
        self.download_confirm_label.configure( text=f"Error downloading file: {e}" )
    except Exception as e:
        self.download_confirm_label.configure( text=f"An unexpected error occurred: {e}" )
    
    # Enable 'Next' button
    populate_subtitle_frame( self.controller.frames['SubtitlePage'], "en" )

#
#
#

#
# Subtitle Page
#

def auth_opensubs( self, language ):
    # authenticate with opensubtitles
    url = "https://api.opensubtitles.com/api/v1/login"

    payload = {
        "username": self.controller.api_data[2],
        "password": self.controller.api_data[3]
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "MovieMatch v0.1a1",
        "Accept": "application/json",
        "Api-Key": self.controller.api_data[1]
    }
    return requests.post( url, json=payload, headers=headers )

def populate_subtitle_frame( self, language ):

    # NEED TO ADD EXCEPTION FOR WHNE NO RESULTS COME BACK FROM OPENSUBTITLES

    # delete old buttons from frame
    if ( len(self.subtitle_frame_buttons) ):
        for button in self.subtitle_frame_buttons:
            button.destroy()
        self.subtitle_frame_buttons.clear()

    # authenticate with opensubtitles
    response = auth_opensubs( self, language )
    if( response.status_code == 200 ):
        token = response.json()['token']

        # Search for movie subs
        url = "https://api.opensubtitles.com/api/v1/subtitles"

        querystring = {"tmdb_id":self.controller.tmdb_id,"languages":language,"trusted_sources":"include"}

        headers = {
            "User-Agent": "MovieMatch v0.1a1",
            "Api-Key": self.controller.api_data[1]
        }
        response = requests.get(url, headers=headers, params=querystring)
        language = response.json()['data'][0]['attributes']['language']
        
        # add new buttons to frame
        for i, item in enumerate( response.json()['data'] ):
            file_id = item['attributes']['files'][0]['file_id']
            filename = item['attributes']['files'][0]['file_name']
            button = ctk.CTkButton( self.subtitle_frame, text=filename,
                                    command=lambda id=file_id,name=filename:download_subtitle( self, self.controller.api_data[1], token, id, language, name) )
            button.grid( row=i, column=0, padx=5, pady=(5,5), sticky="ew" )
            self.subtitle_frame_buttons.append( button )
        self.controller.next_button.configure(state="normal")
        self.controller.next_frame = "SubtitlePage"
        return True
    else:
        print( 'ERROR' )
        # OPEN POPUP WINDOW TO EXPLAIN ISSUE, PROVIDE CHANCE TO ENTER CREDENTIALS
        self.subtitle_frame.grid_forget()
        self.status_msg.configure( text="Please enter a valid Opensubtitles API key, username and password to download subtitles..." )
        self.controller.next_button.configure(state="normal")
        self.controller.next_frame = "CompressionPage"

def download_subtitle( self, opensubtitles_api_key, token, id, language, name ):
    self.controller.next_button.configure(state="disabled")

    # get download URL
    url = "https://api.opensubtitles.com/api/v1/download"

    payload = { "file_id": id }
    headers = {
        "User-Agent": "MovieMatch v0.1a1",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Api-Key": opensubtitles_api_key,
        "Authorization": "Bearer " + token
    }

    response = requests.post(url, json=payload, headers=headers)
    download_url = response.json()["link"]

    # download file
    download_path = self.controller.folderpath + '/' + self.controller.movie_name + f"/{name}.{language}.srt"
    try:
        # Send a GET request to the URL
        response = requests.get(download_url, stream=True) # Use stream=True for large files

        # Raise an HTTPError for bad responses (4xx or 5xx)
        response.raise_for_status()

        # Open the local file in binary write mode
        with open(download_path, 'wb') as file:
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:  # Filter out keep-alive new chunks
                    file.write(chunk)
        self.status_msg.configure( text=f"File downloaded successfully to: {download_path}" )

    except requests.exceptions.RequestException as e:
        self.status_msg.configure( text=f"Error downloading file: {e}" )
    except Exception as e:
        self.status_msg.configure( text=f"An unexpected error occurred: {e}" )
    
    self.controller.reset()
#
#
#