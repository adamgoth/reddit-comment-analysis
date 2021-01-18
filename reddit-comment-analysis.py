# imports
import requests  # The requests library for HTTP requests in Python

# globals
comment_count = 0
comment_array = []
more_comment_ids = []

# define helper functions


def analyze_words(words):
    analysis_string = words.split(' ')
    word_dict = {}
    for word in analysis_string:
        cleaned_word = word.replace('.', '').replace("'", '').replace(
            '\n', '').replace(',', '').replace("’", '').lower()
        if cleaned_word not in word_dict:
            word_dict[cleaned_word] = 1
        else:
            word_dict[cleaned_word] += 1

    return word_dict


def sanitize_input(url):
    last_char = url[-1]
    if last_char == '/':
        url = url[:-1]
    url = f'{url}.json'
    return url


def create_thread_url(comment_id):
    return sanitized_thread_url.replace('.json', f'/{comment_id}.json')


def parse_children_for_comments(children):
    global comment_count
    global comment_array
    for child in children:
        if child['kind'] == "more":
            children = child['data']['children']
            for id in children:
                more_comment_ids.append(id)
        if child['kind'] == "t1":
            comment_count += 1
            comment_array.append(child['data']['body'])
            get_replies(child['data'])


def get_replies(comment):
    global comment_count
    if comment['replies'] != "":
        children = comment['replies']['data']['children']
        parse_children_for_comments(children)


# get url from user
print('enter the reddit post url (e.g. https://www.reddit.com/r/redditdev/comments/krolrb/multicomments/):')
thread_url = input()

# pass user's url to sanitize helper
sanitized_thread_url = sanitize_input(thread_url)

# make network call
req_data = requests.get(sanitized_thread_url, headers={
                        'User-agent': 'adamgoth.com'})

if req_data.status_code != 200:
    print('request failed')
    print(req_data.json())

if req_data.status_code == 200:
    json_data = req_data.json()
    for item in json_data:
        children = item['data']['children']
        parse_children_for_comments(children)

# handle extra comment ids
for id in more_comment_ids:
    req_data = requests.get(create_thread_url(
        id), headers={'User-agent': 'adamgoth.com'})
    if req_data.status_code != 200:
        print('request failed')
        print(req_data.json())

    if req_data.status_code == 200:
        json_data = req_data.json()
        for item in json_data:
            children = item['data']['children']
            parse_children_for_comments(children)

comment_string = ' '.join(comment_array)
results = analyze_words(comment_string)

sorted = sorted(results.items(), key=lambda x: x[1], reverse=True)

print(f'{comment_count} comments analyzed')

for key in sorted:
    print(key)
