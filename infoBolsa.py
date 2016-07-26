# Import the necessary methods from "twitter" library
import twitter
import unittest
import json
import queue

# Variables that contains the user credentials to access Twitter API
class tweetComp():
  def __init__(self,tweet):
    self.tweet=tweet
    self.priority=[tweet.favorite_count,tweet.retweet_count]

  def __lt__(self,other):
    return (self.priority[0],self.priority[1])<(other.priority[0],other.priority[1])
  def __comp__(self,other):
    return comp((self.priority[0],self.priority[1])<(other.priority[0],other.priority[1]))

class infBolsa():
  def __init__(self):
    self.texts=set([])
    self.ids=set([])
    self.tweets=queue.PriorityQueue()
    self.api= twitter.Api(
    consumer_key = 'psPRnpYkwCJP1zkuKKIp6A18h',
    consumer_secret = '3kOkRIcPeyN1CmzUTgVjB5ESDmlliwDcBwbyQxolMxGnNmgrmD',
    access_token_key = '750445380819640321-p1vufLPwUJaKr75SSJTIpvOwvlxkjHJ',
    access_token_secret = '8l4Me33FefOTRc0YO6KSIlFFR6L3X46itnGYpcJnSN3pc')

  def informacionTwitter(self):
    self.topTweets=self.api.GetSearch(term="(#stockmarket #stocks 'stock market')",count=5)
    self.paises=['peru','U.S.','united states','spain','latin america']
    self.topTweets+=self.api.GetSearch(term="'stocks market' Financial crisis",count=5)
    self.topTweets+=self.api.GetSearch(term="'stocks market' #news",count=5)
    for pais in self.paises:
      self.topTweets+=self.api.GetSearch(term="'stocks market' "+ pais ,count=3)

  def inserting(self,tweet):
    if (tweet.text in self.texts) == False:
      self.texts.add(tweet.text)
      tw=tweetComp(self.api.GetStatus(tweet.id))
      self.ids.add(tweet.id)
      self.tweets.put(tw)

  def ordenar(self):
    for tweet in self.topTweets:
      if(tweet.retweeted_status)==None:
        self.inserting(tweet)
      else:
        if (tweet.retweeted_status.id in self.ids) == False:
          self.inserting(tweet.retweeted_status)
  def actualizarDatos(self):
    self.informacionTwitter()
    self.ordenar()
