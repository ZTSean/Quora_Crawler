from user import User
from nquora import Quora
from bs4 import BeautifulSoup
from selenium import webdriver
import codecs
import time
import Queue

## Settings -----------------------------------
username = 'example@gmail.com'
password = '111111'
total_users_to_read = 10000
current_read_users = 0
users_to_read_queue = Queue.Queue()
user_stats = [] ## final users stats to store

## Get answer for top users in Quora in 2017
url = 'https://www.quora.com'
question = 'Which-are-the-top-10-most-followed-accounts-on-Quora'
author = 'Anmol-Jamwal-2'
answer = Quora.get_one_answer(question, author) # question and answer are variables

print '---------------------------------'
### READING USERS INFO UNTIL TOTAL NUMBER REACH THE THRESHOLD ===================================
## Search users in the list of answer
print 'Start collecting user name of top users from dictionary...'
soup = BeautifulSoup(answer['answer'], 'html.parser')

user_span = soup.find_all('span', class_='qlink_container')

user_name_list = []
for item in user_span:
    name = str(item.find('a', href=True)['href'].split('/')[2])
    #user_name_list.append(name)
    users_to_read_queue.put(name)

#users_to_read_queue.put(user_name_list[1])

print users_to_read_queue.qsize()

print "Got all top user names..."
print '---------------------------------'
print 'Start collecting user profile data...'

driver = webdriver.PhantomJS()
driver.get('http://www.quora.com/profile/Robert-Scoble-1/followers')

## check log in
User.check_login(driver, username, password)

while not users_to_read_queue.empty():
    ## every time read k(total number of people in the list) people, read level by level
    for i in range(users_to_read_queue.qsize()):
        name = users_to_read_queue.get()
        #print name
        user = User(name)
        if user.stats:
            user_stats.append(user.stats)
            current_read_users = current_read_users + 1

            ## append his/her followers to the to_read_queue

            followers = User.get_followers(driver, name, username, password)
            print "# of followers for " + name + ": " + str(len(followers))
            map(users_to_read_queue.put, followers)

        print current_read_users
        if current_read_users > total_users_to_read:
            print "Reach threshold"
            break
        else:
            print "not reach threshold"
    if current_read_users > total_users_to_read:
        break

'''

for user_name in user_name_list:
    i = i+1
    print i
    user = User(user_name)
    if user.stats:
        user_stats.append(user.stats)
        current_read_users = current_read_users + 1
    if i > 1:
        break

'''
print 'Done with collecting user stats: ' + str(len(user_stats))


print '---------------------------------'
### STORE DATA TO LOCAL FILE ===================================
print 'Start writing collected data into local file...'


output_file_name = 'quora_user_stats.csv'
f = open(output_file_name, 'w')

## write headers to the csv file
f.write('username,edits,followers,name,questions,following,blogs,posts,topics,answers\n')
for s in user_stats:
    f.write(s['username'] + ',')
    f.write(str(s['edits']) + ',')
    f.write(str(s['followers']) + ',')
    f.write(s['name'] + ',')
    f.write(str(s['questions']) + ',')
    f.write(str(s['following']) + ',')
    f.write(str(s['blogs']) + ',')
    f.write(str(s['posts']) + ',')
    f.write(str(s['topics']) + ',')
    f.write(str(s['answers']) + '\n')
f.close()
print 'Done with local file writing...'

'''
print '---------------------------------'
print 'Start collecting followers info...'
user = User(author)
print len(user.followers)


driver = webdriver.Chrome()
driver.get('https://www.quora.com/profile/Robert-Scoble-1/followers')





time.sleep(1)
driver.get('https://www.quora.com/profile/Robert-Scoble-1/followers')

f = codecs.open('followers.log', 'w', 'utf-8')
f.write(BeautifulSoup(driver.page_source).prettify())
f.close()

## grad each follower's info, append to queue
soup = BeautifulSoup(driver.page_source)
soup.find('div', class_='UserConnectionsFollowersList').find_all('a', class_='user', href=True)

'''


driver.close()