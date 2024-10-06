from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from newsapi import NewsApiClient
from nltk.sentiment import SentimentIntensityAnalyzer
from bs4 import BeautifulSoup
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from nltk.corpus import stopwords
from collections import Counter
from helper import custom_stop_words

# Sets up NewsAPI and all available sources
app = Flask(__name__)
newsapi = NewsApiClient(api_key="233e756218df4eac9f3965515666e465")
source_dict = newsapi.get_sources()

# Filter sources based on language
english_sources = [
    source for source in source_dict["sources"] if source["language"] == "en"
]
source_names = [source["name"] for source in english_sources]

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Home page
@app.route("/")
def index():
    return render_template("index.html", sources=source_names)


# About page
@app.route("/about")
def about():
    # Finds descriptions, pulled from NewsAPI service.
    source_descriptions = [
        source["description"]
        for source in source_dict["sources"]
        if source["language"] == "en"
    ]
    sources = dict(zip(source_names, source_descriptions))
    return render_template("about.html", sources=sources)


# Breaking News page
@app.route("/breaking")
def breaking():
    try:
        # Fetch a collection of articles from CNN, Fox News, and Reuters
        all_top_headlines = newsapi.get_top_headlines(
            language="en", sources="cnn,fox-news,reuters"
        )

        # Extract just the article section from data
        articles = all_top_headlines["articles"]

        # Gathers URLs from each article and prepares them for text processing.
        article_urls = [article["url"] for article in articles]
        print(article_urls)
        article_text = ""  # Sets up empty article text for initial use
        error_occurred = False  # Flag to indicate if an error occurred

        # Iterate over the list of articles and creates a long string of all the text to be analyzed
        for article_url in article_urls:
            try:
                print(f"Processing and gathering text from article: {article_url}")
                new_text = find_text_in_url(article_url)
                # If it didn't fail to find text (returned None), append this to the existing string of the article's text
                if new_text is not None:
                    article_text += new_text
                else:
                    print(f"Failed to gather text. Skipping article: {article_url}")

            # Catching errors
            except Exception as e:
                print(f"Error finding text in article: {str(e)}")
                error_occurred = True

        # Catching errors
        if error_occurred:
            raise Exception("Error finding text in articles.")

        # Get the top words
        print("Attempting to get top words")
        top_words = get_top_words(article_text)

        # Pass the top words to the template
        return render_template(
            "breaking.html", top_words=top_words, sources=source_names
        )

    except Exception as e:
        # Handle exceptions (e.g., API request limit exceeded)
        return render_template("error.html", sources=source_names, error=str(e))


# Search Results page
@app.route("/search", methods=["GET", "POST"])
def search():
    # Collects user's search query.
    if request.method == "POST" or (request.method == "GET" and "q" in request.args):
        search_query = (
            request.form.get("q") if request.method == "POST" else request.args.get("q")
        )

        # If a search query was inputted:
        if search_query:
            # Take out trailing/leading spaces
            search_query = search_query.strip()
            print("Searching for:", search_query)

            # Scrape and calculate sentiment
            results = scrape(search_query)
            print("results:", results)

            # Clear selected_sources after each search
            session["selected_sources"] = []

            # If results do not load, load an error message.
            if results is None:
                return render_template(
                    "search.html",
                    error="Error loading results. Request limit likely reached for the day.",
                    sources=source_names,
                )

            print("Results.items():", results.items())

            # Load actual scores into dictionary to prepare them to be implemented
            percents = {name: round(score) for name, score in results.items()}

            # Allows for access into functions in python.
            context = {
                "percents": percents,
                "get_sentiment_range": get_sentiment_range,
                "get_sentiment_description": get_sentiment_description,
            }

            # Loads search results
            return render_template(
                "search.html",
                **context,
                sources=source_names,
                search_query=search_query,
            )

        # If there was a lack of a query:
        else:
            return render_template(
                "search.html",
                error="Please enter a search query.",
                sources=source_names,
            )

    # If the user happened to go to XYZ.com/search by typing it into their browser
    else:
        return redirect("/")


# Allows user to select sources for use
@app.route("/update_sources", methods=["POST"])
def update_sources():
    # Saves selected sources to session for use across different functions
    data = request.get_json()
    selected_sources = data.get("sources", [])
    session["selected_sources"] = selected_sources

    print("Selected sources:", selected_sources)

    return "OK"


# Grabs all source names
@app.route("/get_sources")
def get_sources():
    return source_names


# Queries NewsAPI for URLs containing phrase and calculates sentiment
def scrape(search_query):
    # Grabs preferences from settings
    source_names = session.get("selected_sources", [])
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    default_sources = ["cnn", "fox-news", "reuters"]

    # Aligns the name of the source with the id of the source
    source_name_to_id = {
        source["name"]: source["id"] for source in source_dict["sources"]
    }

    try:
        # Check to see if the user has inputted any specific preferences for sources
        if source_names is not None and source_names != []:
            source_list = [source_name_to_id.get(id) for id in source_names]
        # If not, just use the default sources
        else:
            source_list = default_sources

        print("Using sources: ", source_list)

        # Put sources into appropriate format for get_everything()
        sources = ", ".join(source_list)

        # Pulls article results containing query from NewsAPI
        if start_date is None and end_date is None:
            results = newsapi.get_everything(
                q=search_query, sources=sources, from_param=start_date, to=end_date
            )
        elif start_date is None:
            results = newsapi.get_everything(
                q=search_query, sources=sources, to=end_date
            )
        elif end_date is None:
            results = newsapi.get_everything(
                q=search_query, sources=sources, from_param=start_date
            )

        if results is None:
            return None

    except Exception as e:
        # Print the exception details
        import traceback

        traceback.print_exc()

        # Return None to indicate the error
        return None

    # Grab just the articles from the results
    articles = results["articles"]
    sentiments_dict = {}
    sid = SentimentIntensityAnalyzer()

    for article in articles:
        print(article["source"]["name"])
        print(article["url"])
        # Find the URL of every article and their respective source name
        source_url = article["url"]
        source_name = article["source"]["name"]

        try:
            # Use BeautifulSoup to grab all text in the URL
            content = find_text_in_url(source_url)

            # Error occurred
            if content is None:
                raise Exception("Skipping URL.")

        except Exception as e:
            print(f"Error getting content from URL: {str(e)}")
            continue

        # Perform sentiment analysis for each content separately
        sentiment = (sid.polarity_scores(content)["compound"] + 1) * 50

        print(sentiment)
        # Store the sentiment analysis result in the dictionary, but average last result if it already exists
        if source_name in sentiments_dict:
            sentiments_dict[source_name] = (
                sentiments_dict[source_name] + sentiment
            ) / 2
        else:
            sentiments_dict[source_name] = sentiment

    return sentiments_dict


# Finds text within URLs
def find_text_in_url(url, timeout=5):
    # Domains are excluded for being irrelevant or frequently taking too long to load
    excluded_domains = [
        "removed.com",
        "disneyparks.disney.go.com",
        "cnnespanol.cnn.com",
    ]

    # Checks if URL is apart of the domain
    if any(domain in url for domain in excluded_domains):
        print(
            "Link is apart of excluded domains (irrelevant or repeatedly causes issues)."
        )
        return None
    else:
        # Set up retries with a maximum of 3 retries
        retries = Retry(
            total=3, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retries)
        session = requests.Session()
        session.mount("https://", adapter)

        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()  # Raise an error for bad responses (4xx and 5xx)

            # Grab text from URL
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                text = soup.get_text()
                return text
            else:
                raise Exception(
                    "Error: Non-200 status code"
                )  # Raise an exception for non-200 status codes
        except requests.exceptions.Timeout:
            print(f"Timeout occurred for URL: {url}")
            return None  # Return None to indicate timeout
        except Exception as e:
            print(f"Error during request: {str(e)}")
            return None  # Return None for other errors


# Used for ring color in results page
def get_sentiment_range(score):
    if 0 <= score <= 20:
        return "0-20"
    elif 21 <= score <= 40:
        return "21-40"
    elif 41 <= score <= 60:
        return "41-60"
    elif 61 <= score <= 80:
        return "61-80"
    elif 81 <= score <= 100:
        return "81-100"
    else:
        return ""


# Used for description of score in results page
def get_sentiment_description(score):
    if 0 <= score <= 20:
        return "Mostly Negative"
    elif 21 <= score <= 40:
        return "Somewhat Negative"
    elif 41 <= score <= 60:
        return "Neutral"
    elif 61 <= score <= 80:
        return "Somewhat Positive"
    elif 81 <= score <= 100:
        return "Mostly Positive"
    else:
        return ""


# Calculates the most words used in top headlines but filters out words that are irrelevant
def get_top_words(text):
    # Tokenize the text and remove stopwords
    stop_words = set(stopwords.words("english"))
    words = [
        word.lower()
        for word in text.split()
        if word.isalpha()
        and word.lower() not in stop_words
        and word.lower() not in custom_stop_words
    ]

    # Count the occurrences of each word
    word_counts = Counter(words)

    # Get the top 5 most common words
    top_words = word_counts.most_common(5)
    print(top_words)
    return top_words
