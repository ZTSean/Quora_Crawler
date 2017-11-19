#coding=utf-8

from bs4 import BeautifulSoup
import re
import requests
import locale

####################################################################
# Helpers
####################################################################
def try_cast_int(s):
    """ (str) -> int
    Look for digits in the given string and convert them to the required number.
    ('2 upvotes') -> 2
    ('2.2k upvotes') -> 2200
    """
    try:
        pattern = re.compile(r'([0-9]+(\.[0-9]+)*[ ]*[Kk])|([0-9]+)')
        raw_result = re.search(pattern, s).groups()
        if raw_result[2] != None:
            print "2 is not none"
            return int(raw_result[2])
        elif raw_result[1] == None:
            print "1 is none"
            raw_result = re.search(r'([0-9]+)', raw_result[0])
            return int(raw_result.groups()[0]) * 1000

        raw_result = re.search(r'([0-9]+)\.([0-9]+)', raw_result[0])
        #####
        print "aaa"
        if raw_result:
            raw_result = raw_result.groups()
            print "hahahaha"
            return int(raw_result[0]) * 1000 + int(raw_result[1]) * 100
        else:
            print "not a K style"

        return locale.atoi(s)
    except:
        return s

def try_cast_int_comma(s):
    '''
    (str) -> int
    example: ('78,769') -> 78769
    :param s: the input string to be cast
    :return: int
    '''
    try:
        return int(s.replace(',', ''))
    except:
        return s
def get_question_link(soup):
    """ (soup) -> str
    Returns the link at which the question can is present.
    """
    question_link = soup.find('a', attrs = {'class' : 'question_link'})
    return 'http://www.quora.com' + question_link.get('href')

def get_author(soup):
    """ (soup) -> str
    Returns the name of the author
    """
    return soup.find('div', class_='feed_item_answer_user').find('a', class_='user').string

def extract_username(username):
    """ (soup) -> str
    Returns the username of the author
    """
    if 'https://www.quora.com/' not in username['href']:
        return username['href'][1:]
    else:
        username = re.search("[a-zA-Z-\-]*\-+[a-zA-Z]*-?[0-9]*$", username['href'])
        if username is not None:
            return username.group(0)
        else:
            return None

####################################################################
# API
####################################################################
class Quora:
    """
    The class that contains functions required to fetch details of questions and answers.
    """
    @staticmethod
    def get_one_answer(question, author=None):
        """ (str [, str]) -> dict
        Fetches one answer and it's details.
        """
        if author is None: # For short URL's
            if re.match('http', question): # question like http://qr.ae/znrZ3
                soup = BeautifulSoup(requests.get(question).text)
            else: # question like znrZ3
                soup = BeautifulSoup(requests.get('http://qr.ae/' + question).text)
        else:
            soup = BeautifulSoup(requests.get('http://www.quora.com/' + question + '/answer/' + author).text)
        return Quora.scrape_one_answer(soup)

    @staticmethod
    def scrape_one_answer(soup):
        """ (soup) -> dict
        Scrapes the soup object to get details of an answer.
        """
        try:
            answer = soup.find('div', id=re.compile('_answer_content$')).find('span', class_='rendered_qtext')
            print answer
            
            question_link = get_question_link(soup)
            print question_link
            
            author = get_author(soup)
            print author
            
            views = soup.find('span', attrs = {'class' : 'meta_num'}).string
            print views

            #want_answers = soup.find('span', attrs = {'class' : 'count'}).string no longer exist

            count = 0
            try:
                upvote_count = soup.find('a', attrs = {'class' : 'VoterListModalLink AnswerVoterListModalLink'}).string

                ## example: u'16 Upvotes'
                if upvote_count is not None:
                    count = upvote_count.split()[0] ## get the number
            except:
                count = 0

            print count

            '''
            # no longer work
            try:
                comment_count = soup.find_all('a', id = re.compile('_view_comment_link'))[-1].find('span').string
                # '+' is dropped from the number of comments.
                # Only the comments directly on the answer are considered. Comments on comments are ignored.
            except:
                comment_count = 0
            '''

            answer_stats = map(try_cast_int, [views, count])

            answer_dict = {'views' : answer_stats[0],
                           #'want_answers' : answer_stats[1],
                           'upvote_count' : answer_stats[1],
                           #'comment_count' : answer_stats[3],
                           'answer' : str(answer),
                           'question_link' : question_link,
                           'author' : author
                          }
            return answer_dict
        except:
            return {}

    @staticmethod
    def get_latest_answers(question):
        """ (str) -> list
        Takes the title of one question and returns the latest answers to that question.
        """
        soup = BeautifulSoup(requests.get('http://www.quora.com/' + question + '/log').text)
        authors =  Quora.scrape_latest_answers(soup)
        return [Quora.get_one_answer(question, author) for author in authors]

    @staticmethod
    def scrape_latest_answers(soup):
        """ (soup) -> list
        Returns a list with usernames of those who have recently answered the question.
        """
        try:
            authors = []
            clean_logs = []
            raw_logs = soup.find_all('div', attrs={'class' : 'feed_item_activity'})

            for entry in raw_logs:
                if 'Answer added by' in entry.next:
                    username = entry.find('a', attrs={'class' : 'user'})
                    if username is not None:
                        username = extract_username(username)
                        if username not in authors:
                            authors.append(username)
            return authors
        except:
            return []

    @staticmethod
    def get_question_stats(question):
        """ (soup) -> dict
        Returns details about the question.
        """
        soup = BeautifulSoup(requests.get('http://www.quora.com/' + question).text)
        return Quora.scrape_question_stats(soup)

    @staticmethod
    def scrape_question_stats(soup):
        """ (soup) -> dict
        Scrapes the soup object to get details of a question.
        """
        try:
            raw_topics = soup.find_all('span', attrs={'TopicNameSpan'})
            topics = []
            for topic in raw_topics:
                topics.append(topic.string)

            #want_answers = soup.find('span', attrs={'class' : 'count'}).string
            answer_count = soup.find('div', attrs={'class' : 'answer_count'}).next.split()[0]
            print ("answer_count:" + answer_count)
            question_text = list(soup.find('div', attrs = {'class' : 'question_text_edit'}).find('h1').children)[-1]
            #question_details = soup.find('div', attrs = {'class' : 'question_details_text'}) no longer exist
            answer_wiki = soup.find('div', attrs = {'class' : 'AnswerWikiArea'}).find('div')
            print type(answer_count)
            print try_cast_int(answer_count)
            question_dict = { #'want_answers' : try_cast_int(want_answers), // not find in current UI design
                             'answer_count' : try_cast_int(answer_count),
                             'question_text' : question_text.string,
                             'topics' : topics,
                             #'question_details' : str(question_details),
                             'answer_wiki' : str(answer_wiki),
                            }

            return question_dict
        except:
            return {}

    ### Legacy API
    @staticmethod
    def get_user_stats(u):
        """ (str) -> dict
        Deprecated. Use the User class.
        """
        from user import User
        return User.get_user_stats(u)

    @staticmethod
    def get_user_activity(u):
        """ (str) -> dict
        Deprecated. Use the User class.
        """
        from user import User
        return User.get_user_activity(u)

    @staticmethod
    def get_activity(u):
        """ (str) -> dict
        Deprecated. Use the User class.
        """
        from user import User
        return User.get_activity(u)
