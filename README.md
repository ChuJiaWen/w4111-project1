## w4111-project1
PostgreSQL account: xg2399

## The URL of our web application:
[http://34.172.178.48:8111/](http://34.172.178.48:8111/)

## Features:
1. Parts of the original proposal in Part 1 that have been implemented: 
* Create albums
* Upload photos into albums
* Add friends
* Filter photos by tags
* Comment and like photos

2. New features: 
* Search photos according to tag
* Search commenter according to comment
* See popular photos in the home page

## Two of the web pages that require the most interesting database operations:  
1. The /browse page allows the user to view photos uploaded by other users. By going into the browse page, the current user ID was used to retrieve the albums of users that are either a public account or a private account but are friends of the current user. I think it is interesting because it allows the users to choose how their account will be used only to share with friends or share with all other users on the platform.

2. The /friend page not only allows users to search friends by name, email, and hometown, but this page also shows friend recommendations. The recommendation system works as follows: the input is the current user id; get all the friends of the current user’s friends who are not friends with the current user yet, then list out all this user for recommendation. I think it is interesting because the recommendation might recommend some people who you might know already but not friends yet.
