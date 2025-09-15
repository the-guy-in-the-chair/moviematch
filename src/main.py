from cryptography.fernet import Fernet, InvalidToken
import customtkinter as ctk
import threading
import modules
import json
import os
import re

version = "v0.1a1"

#
# CURR TASK:
# fix TMDB key encryption mess
# complete compression page (alpha state)
#
# NEXT TO-DO:
# file: main.py
# task: need to figure out TMDB folder name issue, extras need to be scanned first,
# then folder made after
#

class Main( ctk.CTk ):
    def __init__( self, *args, **kwargs ):
        ctk.CTk.__init__( self, *args, **kwargs )

        # app settings
        ctk.set_appearance_mode( "system" )
        self.title( "MovieMatch " + version )
        self.geometry( "600x480" )
        # FIND BETTER SOLUTION to icon problem
        try:
            self.iconbitmap( "./_internal/imgs/icon.ico" )
        except:
            self.iconbitmap( "./imgs/icon.ico" )
        self.grid_rowconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=1, weight=1 )

        # Frame container for each 'page'
        self.container = ctk.CTkFrame( self )
        self.container.grid( row=0, column=0, columnspan=2, padx=0, pady=0, sticky="nsew" )
        self.container.grid_rowconfigure( index=0, weight=1 )
        self.container.grid_columnconfigure( index=0, weight=1 )

        # Retrieving encryption key
        try:
            # Load the key
            with open('./data/secret.key', 'rb') as key_file:
                key = key_file.read()
        except FileNotFoundError:
            # Generate and save a key (do this once and keep the key secure)
            key = Fernet.generate_key()
            with open('./data/secret.key', 'wb') as key_file:
                key_file.write(key)
        self.cipher_suite = Fernet(key)

        # Retrieving and decrypting secrets
        # ['7941d3593a255b0c15f6d5c86088f9e7', 'PPwbSkMsK0JwYmk2uwdFgrNed0TC44c9', 'limejellosubs', 'John3602!']
        self.tmdb_api_key = ''
        self.opensubs_api_key = ''
        self.opensubs_username = ''
        self.opensubs_password = ''
        self.api_data = ['','','','']
        try:
            with open( "./data/api_data.txt", 'rb' ) as rf:
                encrypted_data = rf.read()
                self.api_data = (self.cipher_suite.decrypt( encrypted_data ).decode()).split('#')
                self.tmdb_api_key = self.api_data[0]
                self.opensubs_api_key = self.api_data[1]
                self.opensubs_username = self.api_data[2]
                self.opensubs_password = self.api_data[3]
        except (InvalidToken, FileNotFoundError):
            print( 'error' )
            """data = self.api_data[0] + '#' + self.api_data[1] + '#' + self.api_data[2] + '#' + api_data[3]
            with open( "./data/api_data.txt", 'wb' ) as wf:
                wf.write( cipher_suite.encrypt(data.encode('utf-8')) )"""
        
        # API Key Check
        if ( modules.test_api_key( self, self.tmdb_api_key ) ):
            self.next_frame = "MediaSearchPage"
        else:
            self.next_frame= "APIKeyPage"

        # Options button
        ## Load in saved settings
        with open( "data/options.json", 'r+' ) as f:
            try:
                self.data = json.load( f )
            except json.decoder.JSONDecodeError:
                self.data = {
                    'Preview Samples':'6',
                    'Preview Sample Duration':'10', # in seconds
                    'Main Feature Target Video Bitrate':'10000', # in kbps
                    'Extras Target Video Bitrate':'5000', # in kbps
                    'Video Bitrate Delta':'1000' # in kbps
                }
                json.dump(self.data, f)
        f.close()
        self.options_window = None
        self.options_button = ctk.CTkButton( self, text="Options", command=self.launch_options )
        self.options_button.grid( row=1, column=0, padx=0, pady=0, sticky="w" )

        # Next button
        self.next_button = ctk.CTkButton( self, text="Next", command=self.next_page, state="disabled" )
        self.next_button.grid( row=1, column=1, padx=0, pady=0, sticky="e")

        # important variables/lists
        self.files = [] # format: [duration (seconds), filepath, file-type]
        self.extras = [] # format: [duration (seconds), name, extra-type]
        self.movie_name= ""
        self.disc_type = ""
        self.tmdb_id = ""
        self.folderpath = ""

        # Load presets
        self.presets = {}
        # get files in preset folder
        directory_contents = os.listdir( './presets' )
        # check to make sure they are presets
        container_types = re.compile( r'\.json' )
        for item in directory_contents:
            file_type = container_types.search(item)
            if ( file_type ):
                with open( './presets/' + item ) as f:
                    json_data = json.load( f )
                # get the name PresetName
                preset_name = json_data['PresetList'][0]['PresetName']
                # add the list [presetname, folderpath] to the presets list
                self.presets[preset_name] = './presets/' + item

        self.pages = ( APIKeyPage, MediaSearchPage, FileMatchPage, PosterSelectPage, SubtitlePage )
        self.frames = {}
        for page in self.pages:
            page_name = page.__name__
            frame = page( parent=self.container, controller=self )
            self.frames[page_name] = frame
            frame.grid( row=0, column=0, pady=10, padx=10, sticky="nsew")

        # control which frame is shown (for testing)
        #self.next_frame = "CompressionPage"
        self.show_frame( self.next_frame )
    
    def show_frame( self, page_name ):
        frame = self.frames[ page_name ]
        frame.tkraise()
    def next_page( self ):
        print( self.next_frame )
        self.next_button.configure( state="disabled", text="Next" )
        self.show_frame( self.next_frame )
    def reset( self ):
        for frame in self.frames:
            self.frames[frame].destroy()
        self.frames = {}
        self.pages = ( APIKeyPage, MediaSearchPage, FileMatchPage, PosterSelectPage, SubtitlePage )
        for page in self.pages:
            page_name = page.__name__
            frame = page( parent=self.container, controller=self )
            self.frames[page_name] = frame
            frame.grid( row=0, column=0, pady=10, padx=10, sticky="nsew")
        self.files = [] # format: [duration (seconds), filepath, file-type]
        self.extras = [] # format: [duration (seconds), name, extra-type]
        self.movie_name= ""
        self.disc_type = ""
        self.tmdb_id = ""
        self.folderpath = ""
        self.next_button.configure(state="normal", text="Home")
        self.next_frame = "MediaSearchPage"
    def launch_options( self ):
        if self.options_window is None or not self.options_window.winfo_exists():
            self.options_window = OptionsWindow( controller=self )
            self.options_window.protocol( "WM_DELETE_WINDOW", self.save_options )
        self.options_window.focus()
    def save_options( self ):
        # Write out API data
        self.api_data[0] = self.options_window.tmdb_entry.get()
        self.api_data[1] = self.options_window.opensubs_key_entry.get()
        self.api_data[2] = self.options_window.opensubs_user_entry.get()
        self.api_data[3] = self.options_window.opensubs_pass_entry.get()
        modules.write_api_data( self, self.cipher_suite, self.api_data )
        # Write out options
        self.data['Preview Samples'] = self.options_window.preview_samples_entry.get()
        self.data['Preview Sample Duration'] = self.options_window.preview_sample_duration_entry.get()
        self.data['Main Feature Target Video Bitrate'] = self.options_window.mf_target_video_bitrate_entry.get()
        self.data['Extras Target Video Bitrate'] = self.options_window.e_target_video_bitrate_entry.get()
        self.data['Video Bitrate Delta'] = self.options_window.video_bitrate_delta_entry.get()
        with open( "data/options.json", 'w' ) as f:
            json.dump(self.data, f)
        f.close()
        # Close window
        self.options_window.destroy()


class APIKeyPage( ctk.CTkFrame ):
    def __init__( self, parent, controller ):
        # Frame Configuration
        ctk.CTkFrame.__init__( self, parent )
        self.controller = controller
        self.grid_columnconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=1, weight=0 )
        self.grid_rowconfigure( index=0, weight=1 )
        self.grid_rowconfigure( index=1, weight=1 )
        self.grid_rowconfigure( index=2, weight=1 )

        # Building Frame Elements
        self.label = ctk.CTkLabel( self, text="No TMDB API key detected, to get one click the button ->" )
        self.label_button = ctk.CTkButton( self, text="Go To TMDB.com", command=lambda:modules.to_browser() )
        self.entrybox = ctk.CTkEntry( self, placeholder_text="Your TMDB API key goes here...", placeholder_text_color="gray" )
        self.entrybox_button = ctk.CTkButton( self, text="Enter", command=lambda:modules.api_key_submit(self) )
        self.login_state = ctk.CTkLabel( self, text="Logged in successfully!")

        # Adding Elements to Frame
        self.label.grid( row=0, column=0, padx=(20,5), pady=10, sticky="sew" )
        self.label_button.grid( row=0, column=1, padx=(5,20), pady=10, sticky="se" )
        self.entrybox.grid( row=1, column=0, padx=(20,5), pady=10, sticky="new" )
        self.entrybox_button.grid( row=1, column=1, padx=(5,20), pady=10, sticky="ne" )

class MediaSearchPage( ctk.CTkFrame ):
    def __init__( self, parent, controller ):       
        # Frame Configuration
        ctk.CTkFrame.__init__( self, parent )
        self.controller = controller
        self.grid_rowconfigure( index=2, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )

        # variables/lists
        self.results_names = []
        self.results_versions = []
        self.sframe_buttons = []
        self.sub_sframe_buttons = []
        self.html_doc = ""
        self.content = ""

        # building the page elements
        # NOTE: these should pretty much all be instances, not class variables (so self.name instead of name)
        self.folder_path_entry = ctk.CTkEntry( self, placeholder_text="Enter the folder path here...", placeholder_text_color="gray" )
        self.folder_path_button = ctk.CTkButton( self, text="browse", command=lambda:modules.select_directory(self) )
        self.name_entry = ctk.CTkEntry( self, placeholder_text="Enter the media title here...", placeholder_text_color="gray" )
        #self.name_button = ctk.CTkButton( self, text="search", command=lambda:modules.search_for_entry(self, self.name_entry.get()) )
        self.name_button = ctk.CTkButton( self, text="search", command=self.search_submit )
        self.sframe = ctk.CTkScrollableFrame( self, fg_color="gray" )
        self.sub_sframe = ctk.CTkScrollableFrame( self, fg_color="gray" )

        # adding the elements to the page
        self.folder_path_entry.grid( row=0, column=0, padx=0, pady=(10,0), sticky="ew" )
        self.folder_path_button.grid( row=0, column=1, padx=0, pady=(10,0), sticky="ew" )
        self.name_entry.grid( row=1, column=0, padx=0, pady=(10,10), sticky="ew" )
        self.name_button.grid( row=1, column=1, padx=0, pady=(10,10), sticky="ew" )
        self.sframe.grid( row=2, column=0, columnspan=2, padx=0, pady=0, sticky="nsew" )
        self.sframe.grid_columnconfigure( index=0, weight=1 )
    
    def search_submit( self ):
        self.name_button.configure( state='disabled' )
        new_thread = threading.Thread( target=lambda:modules.search_for_entry(self, self.name_entry.get()) )
        new_thread.start()

class FileMatchPage( ctk.CTkFrame ):
    def __init__( self, parent, controller ):
        ctk.CTkFrame.__init__( self, parent )
        self.controller = controller
        self.grid_rowconfigure( index=1, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=1, weight=1 )

        # vars
        self.dest_dir = ""
        self.submenu_selection_id = -1
        self.matched_files = {}
        self.unmatched_files = {}
        self.unmatched_extras = {}
        self.matched_labels = {}
        self.unmatched_labels = {}
        self.extras_labels = {}

        # run file match
        self.run_file_match_button = ctk.CTkButton( self, text="Run File Match", command=lambda:modules.match_files( self ) )
        self.matched_label = ctk.CTkLabel( self, text="Matched Files" )
        self.unmatched_label = ctk.CTkLabel( self, text="Not Matched Files")
        self.matched_frame = ctk.CTkScrollableFrame( self, fg_color="gray" )
        self.unmatched_frame = ctk.CTkScrollableFrame( self, fg_color="gray" )
        self.unmatched_extras_frame = ctk.CTkScrollableFrame( self, fg_color="gray" )

        self.matched_label.grid( row=0, column=0, padx=0, pady=0, sticky="ew" )
        self.unmatched_label.grid( row=0, column=1, padx=0, pady=0, sticky="ew" )
        self.matched_frame.grid( row=1, column=0, padx=(0,5), pady=(0,10), sticky="nsew")
        self.unmatched_frame.grid( row=1, column=1, padx=(5,0), pady=(0,10), sticky="nsew")
        self.run_file_match_button.grid( row=2, column=0, columnspan=2, padx=0, pady=0, sticky="ew" )

class PosterSelectPage( ctk.CTkFrame ):
    def __init__( self, parent, controller ):
        ctk.CTkFrame.__init__( self, parent )
        self.controller = controller
        self.grid_rowconfigure( index=1, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )

        self.poster_select_label = ctk.CTkLabel( self, text="Select a poster:" )
        self.my_sframe = ctk.CTkScrollableFrame( self, fg_color='gray' )
        self.download_confirm_label = ctk.CTkLabel( self, text="" )

        self.image_labels = []

        self.poster_select_label.grid( row=0, column=0, padx=0, pady=10, sticky="w")

class SubtitlePage( ctk.CTkFrame ):
    def __init__( self, parent, controller ):
        ctk.CTkFrame.__init__( self, parent )
        self.controller = controller
        self.grid_rowconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )

        self.subtitle_frame_buttons = []
        self.subtitles = []

        self.subtitle_frame = ctk.CTkScrollableFrame( self, fg_color="gray" )
        self.subtitle_frame.grid( row=0, column=0, padx=0, pady=0, sticky="nsew" )
        self.status_msg = ctk.CTkLabel( self, text="" )
        self.status_msg.grid()
        
class OptionsWindow ( ctk.CTkToplevel ):
    def __init__( self, controller ):
        ctk.CTkToplevel.__init__( self, controller )
        self.controller = controller
        self.title("Options")
        self.geometry("400x300")
        self.grid_rowconfigure( index=0, weight=1 )
        self.grid_columnconfigure( index=0, weight=1 )

        self.main_window = ctk.CTkScrollableFrame( self )
        self.main_window.grid( row=0, column=0, padx=0, pady=0, sticky="nsew")

        vcmd = (self.register(self.callback))
        
        # API options
        self.api_heading = ctk.CTkLabel( self.main_window, text="API Options" )
        self.tmdb_frame = ctk.CTkFrame( self.main_window )
        self.tmdb_label = ctk.CTkLabel( self.tmdb_frame, text="TMDB API Key: " )
        self.tmdb_entry = ctk.CTkEntry( self.tmdb_frame, width=240 )
        self.tmdb_entry.insert( 0, self.controller.api_data[0] )
        self.opensubs_key_frame = ctk.CTkFrame( self.main_window )
        self.opensubs_key_label = ctk.CTkLabel( self.opensubs_key_frame, text="Opensubtitles API Key: " )
        self.opensubs_key_entry = ctk.CTkEntry( self.opensubs_key_frame, width=240 )
        self.opensubs_key_entry.insert( 0, self.controller.api_data[1] )
        self.opensubs_user_frame = ctk.CTkFrame( self.main_window )
        self.opensubs_user_label = ctk.CTkLabel( self.opensubs_user_frame, text="Opensubtitles Username: " )
        self.opensubs_user_entry = ctk.CTkEntry( self.opensubs_user_frame, width=240 )
        self.opensubs_user_entry.insert( 0, self.controller.api_data[2] )
        self.opensubs_pass_frame = ctk.CTkFrame( self.main_window )
        self.opensubs_pass_label = ctk.CTkLabel( self.opensubs_pass_frame, text="Opensubtitles Password: " )
        self.opensubs_pass_entry = ctk.CTkEntry( self.opensubs_pass_frame, width=240 )
        self.opensubs_pass_entry.insert( 0, self.controller.api_data[3] )
        #
        # preview options
        self.preview_heading = ctk.CTkLabel( self.main_window, text="Preview Settings")
        # preview samples
        self.preview_samples_frame = ctk.CTkFrame( self.main_window )
        self.preview_samples_label = ctk.CTkLabel( self.preview_samples_frame, text="Preview Samples: " )
        self.preview_samples_entry = ctk.CTkEntry( self.preview_samples_frame, width=30, validate='all', validatecommand=(vcmd, '%P') )
        self.preview_samples_entry.insert( 0, self.controller.data['Preview Samples'] )
        # preview sample duration
        self.preview_sample_duration_frame = ctk.CTkFrame( self.main_window )
        self.preview_sample_duration_label = ctk.CTkLabel( self.preview_sample_duration_frame, text="Preview Sample Duration: " )
        self.preview_sample_duration_entry = ctk.CTkEntry( self.preview_sample_duration_frame, width=30, validate='all', validatecommand=(vcmd, '%P') )
        self.preview_sample_duration_entry.insert( 0, self.controller.data['Preview Sample Duration'] )
        #
        # bitrate options
        self.bitrate_label = ctk.CTkLabel( self.main_window, text="Bitrate Options" )
        # main feature target video bitrate
        self.mf_target_video_bitrate_frame = ctk.CTkFrame( self.main_window )
        self.mf_target_video_bitrate_label = ctk.CTkLabel( self.mf_target_video_bitrate_frame, text="Main Feature Target Video Bitrate: " )
        self.mf_target_video_bitrate_entry = ctk.CTkEntry( self.mf_target_video_bitrate_frame, width=60, validate='all', validatecommand=(vcmd, '%P') )
        self.mf_target_video_bitrate_entry.insert( 0, self.controller.data['Main Feature Target Video Bitrate'] )
        # extras target video bitrate
        self.e_target_video_bitrate_frame = ctk.CTkFrame( self.main_window )
        self.e_target_video_bitrate_label = ctk.CTkLabel( self.e_target_video_bitrate_frame, text="Extras Target Video Bitrate: " )
        self.e_target_video_bitrate_entry = ctk.CTkEntry( self.e_target_video_bitrate_frame, width=60, validate='all', validatecommand=(vcmd, '%P') )
        self.e_target_video_bitrate_entry.insert( 0, self.controller.data['Extras Target Video Bitrate'] )
        # video bitrate delta
        self.video_bitrate_delta_frame = ctk.CTkFrame( self.main_window )
        self.video_bitrate_delta_label = ctk.CTkLabel( self.video_bitrate_delta_frame, text="Video Bitrate Delta: " )
        self.video_bitrate_delta_entry = ctk.CTkEntry( self.video_bitrate_delta_frame, width=60, validate='all', validatecommand=(vcmd, '%P') )
        self.video_bitrate_delta_entry.insert( 0, self.controller.data['Video Bitrate Delta'] )
        #

        self.api_heading.grid()
        self.tmdb_frame.grid()
        self.tmdb_label.grid( row=0, column=0 )
        self.tmdb_entry.grid( row=0, column=1 )
        self.opensubs_key_frame.grid()
        self.opensubs_key_label.grid( row=0, column=0 )
        self.opensubs_key_entry.grid( row=0, column=1 )
        self.opensubs_user_frame.grid()
        self.opensubs_user_label.grid( row=0, column=0 )
        self.opensubs_user_entry.grid( row=0, column=1 )
        self.opensubs_pass_frame.grid()
        self.opensubs_pass_label.grid( row=0, column=0 )
        self.opensubs_pass_entry.grid( row=0, column=1 )

        self.preview_heading.grid( column=0 )
        self.preview_samples_frame.grid( column=0 )
        self.preview_samples_label.grid( row=0, column=0 )
        self.preview_samples_entry.grid( row=0, column=1 )
        self.preview_sample_duration_frame.grid( column=0 )
        self.preview_sample_duration_label.grid( row=0, column=0 )
        self.preview_sample_duration_entry.grid( row=0, column=1 )
        self.preview_sample_duration_frame.grid( column=0 )
        self.preview_sample_duration_label.grid( row=0, column=0 )
        self.preview_sample_duration_entry.grid( row=0, column=1 )

        self.bitrate_label.grid()
        self.mf_target_video_bitrate_frame.grid()
        self.mf_target_video_bitrate_label.grid( row=0, column=0 )
        self.mf_target_video_bitrate_entry.grid( row=0, column=1 )
        self.e_target_video_bitrate_frame.grid()
        self.e_target_video_bitrate_label.grid( row=0, column=0 )
        self.e_target_video_bitrate_entry.grid( row=0, column=1 )
        self.video_bitrate_delta_frame.grid()
        self.video_bitrate_delta_label.grid( row=0, column=0 )
        self.video_bitrate_delta_entry.grid( row=0, column=1 )
    
    def callback(self, P):
        return str.isdigit(P) or P == ""

if __name__ == "__main__":
    app = Main()
    app.mainloop()