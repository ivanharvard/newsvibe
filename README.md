# NewsVibe

NewsVibe is a website that uses Flask for its backend, and uses HTML, CSS, Javascript, and a little bit of jQuery to control the front end. It allows the user to discover sentiment analysis and trends within recent topics by the use of queries.


## How to Install
1. Run `pip install flask flask_session newsapi-python nltk bs4 requests dotenv os`
2. Download the newsvibe.zip folder
3. Extract the contents and place them in the root of your file manager in your IDE in a file known as "newsvibe"
4. In your terminal, run `cd newsvibe`
5. In your terminal, `flask run`
6. Follow the directions in the terminal to access the link at which you can access the website
7. The structure of your newsvibe folder should look like this:

```
newsvibe
├── static
│   ├── favicon.ico
│   ├── search.png
│   ├── settings.png
│   └── styles.css
├── templates
│   ├── about.html
│   ├── breaking.html
│   ├── error.html
│   ├── index.html
│   ├── layout.html
│   └── search.html
├── app.py
├── helper.py
├── README.md
├── DESIGN.md
```

## How to Use

### Index
When you load up the home page, you will be presented with a searchbar in the center of the screen and in the top right of the navbar. You are allowed to access the searchbar or other pages from here or on any other page, so feel free to explore.

The main function of the website is the sentiment analysis of a query, so I have provided you with some queries that will likely show the capabilities of this website:

1. pfizer
2. Harvard
3. COVID
4. random mumbo jumbo so that the search engine definitely doesn't find any results (yes you can put this exact string in)

Feel free to test your own prompts!

> When you try to load almost any aspect of the page, whether by searching or by accessing a page, a loading screen will appear. Think something's taking too long? Don't worry; if that ring is spinning, there is definitely work going on behind the scenes (as long as you don't interrupt it, of course). You can actually watch the the code print out the things it is doing in the terminal of your IDE. The search engine itself does take a while, which is further explained on why in the DESIGN.md file. The prompts I gave you above are specifically meant to not take long so you can see the most important thing: the results.

You may also want to consider changing the settings of your search. Click the gear icon next to the search icon to have the settings menu appear. You can select any source you wish from here (and search for it too!), as long as it is apart of the NewsAPI service and is primarily in English (which the non-English results are already filtered out for you). You can also change the date range of your articles, although keep in mind that the NewsAPI service only crawls for one-month-old articles, so keep your date ranges within a month from today. Keep everything blank for default settings. Your default sources will be CNN, Fox News, and Reuters. Your settings will be saved even if you X out of the settings menu, or click outside the settings menu area. The settings reset after every search.

### Search
Your results will appear here, and a score from 0-100 is listed to the right inside a colored ring, 0 being the most negative and 100 being the most positive. A 2 word description will be listed next to the source.

### About
You can read a short description about the NewsVibe website here, and read a description of every source that is able to be used on the NewsVibe website. A short description is written under every source, which is pulled from the NewsAPI service.

### Breaking
This page calculates the number of times a specific word occurs in recent top articles from CNN, Fox News, and Reuters. It filters out irrelevant words, like stop-words ('a', 'as', 'it'), page specific words ("businessfox", "tabreuters") or other words that would not be a common topic for a News Source to talk about because it may be too general ("globally", "billion", "celebrity").

You can see the number of times the word appears next to the word. You can also click each of the words which will automatically search the word as a query.

#### Error
An error.html page may replace breaking.html page if there was an error counting the top words or if there was an error with the searching.

## Final Notes
Remember, you can access the searchbar and settings on any page using the navbar, but your settings will be reset with each search. If the loading circle is spinning, the code is still running--even if it doesn't look that way!

The NewsAPI service is limited to 1000 requests per day and since I am using my account for the API key, please try not to use it too much or else you may end up having to wait for the number of requests to reset. General testing should be fine, though. If possible, try not to grade this during the CS50 Fair day, as I may need those requests to showcase my project. If you somehow do end up using 1000 requests in a day, there is an error screen screen to prevent the program from crashing. I considered upgrading but the next plan would be for businesses only and it costs $450/month :(

Happy querying!

## URL

https://youtu.be/HBlQM9oWHA4


