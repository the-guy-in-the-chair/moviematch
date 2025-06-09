from bs4 import BeautifulSoup as bs
import requests
import re

class Extra:
  def __init__(self, runtime, name, type):
    self.runtime = runtime
    self.name = name
    self.type = type

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
  return "-other"

def rms(text):
  """Replaces multiple spaces with a single space in a string.

  Args:
    text: The input string.

  Returns:
    The string with multiple spaces replaced by single spaces.
  """
  return re.sub(r"\s+", " ", text)

user_input = input("Enter movie name: ")
#user_input = "STAR WARS"

url = 'https://www.dvdcompare.net/comparisons/search.php'

payload = {
    'param': user_input,
    'searchtype': 'text'
}

response = requests.post( url=url, data=payload )
html_doc = bs(response.content, 'html.parser')
print()
content = html_doc.body.find('ul', style="list-style-type:none;padding:0;margin-left:0")
content = content.find_all('a')

i = 0
for item in content:
  i += 1
  print ( str(i) + " - " + rms(item.string) )

user_input = input("Enter the correct match: ")
#user_input = 49
selection = content[int(user_input) - 1]['href'].replace('film.php?fid=', '')

url = "https://www.dvdcompare.net/comparisons/film.php?fid=" + selection
print ( url )
html_doc = bs(requests.get(url).content, 'html.parser')
print()

html_doc = html_doc.find('div', id='content')
html_doc = html_doc.find('table')
html_doc = html_doc.find_all('ul')

i = 0
for item in html_doc:
  i += 1
  print( str(i) + " - " + item.li.find('h3').a.get_text(strip=True) )
user_input = input("Enter your edition: ")

html_doc = html_doc[int(user_input) - 1]
#print( html_doc.prettify() )

print()
lists = html_doc.find_all('li')
metadata = {}
for list in lists:
  if ( list.div ):
    #print( list.find('div', class_="label").get_text(strip=True) )
    #print( list.find('div', class_="description").get_text(separator='%', strip=True) )
    data = list.find('div', class_="description").get_text(separator='%', strip=True).split('%')
    metadata[list.find('div', class_="label").get_text(strip=True)] = data
    #if ( list.find('div', class_="label").get_text(strip=True) == "Extras:" ):
      # stuff
print( metadata )
print()

# maybe use basic regex?
extras = []
for item in metadata['Extras:']:
  # string cleaning
  # timecode regex minutes, string number, and possible dash
  num_timecode_regex = re.compile(r'(\d)+:\d\d|(\d)+:\d\d:\d\d')
  str_timecode_regex = re.compile(r'(\s)*\((\d)+:\d\d\)|(\s)*\((\d)+:\d\d:\d\d\)')
  dash_regex = re.compile(r'(\s)*-(\s)+|(\s)+-(\s)*')

  test = num_timecode_regex.search(item)
  test2 = str_timecode_regex.search(item)
  test3 = dash_regex.search(item)

  if ( test and test2 ):
    name = item.replace(test2.group(), "")
    if ( test3 ):
      name = name.replace(test3.group(), "")
    extra_type = findExtraType( name )
    extraObj = Extra( test.group(), name, extra_type )
    extras.append(extraObj)
for item in extras:
  print(str(item.runtime) + " " + item.name + " " + item.type)

# RENAME FILES

path = input("Enter path: ")

for item in extras:
  