# DiscoveryFeed.py
# A news feed for status updates from agents, as well as scientific articles published by agents (or that are preexisting in a given scenario)

import json

class DiscoveryFeed:
    # Constructor
    def __init__(self, filenameIn: str = None):
        # There are two types of posts: scientific discovery articles, and agent status update posts. 
        self.articles = []
        self.updatePosts = []

        # Load the file (if supplied)
        if (filenameIn != None):
            self.loadFromFile(filenameIn)


    #
    # Load articles and update posts from a JSON file
    #
    def loadFromFile(self, filenameIn: str):
        # Load the file
        data = {}
        try:
            with open(filenameIn, 'r') as file:
                data = json.load(file)
        except:
            print("ERROR: DiscoveryFeed: Could not load file containing articles and updates: " + filenameIn)
            exit(1)            

        # Add the articles
        for article in data["articles"]:
            self.articles.append(article)

        # Sort the articles by step (ascending)
        self.articles.sort(key=lambda x: x["step"], reverse=False)

        # Add the update posts
        for post in data["updatePosts"]:
            self.updatePosts.append(post)
        
        # Sort the update posts by step (ascending)
        self.updatePosts.sort(key=lambda x: x["step"], reverse=False)


    #
    #   Add posts
    #
    def addUpdatePost(self, curStep:int, authorName:str, content:str):
        self.articles.append({"step": curStep, "author": authorName, "content": content})

    def addArticle(self, curStep:int, authorName:str, title:str, content:str):
        self.articles.append({"step": curStep, "author": authorName, "title": title, "content": content})

        
    #
    #   Get posts
    #
    def getPosts(self):
        return self.updatePosts
    
    def getArticles(self):
        return self.articles
    

