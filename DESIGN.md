# NewsVibe

NewsVibe is a website that uses Flask for its backend, and uses HTML, CSS, Javascript, and a little bit of jQuery to control the front end. It allows the user to discover sentiment analysis and trends within recent topics by the use of queries.

## Architecture
### Flask Framework

The project is structured as a Flask web application, leveraging its simplicity and extensibility. Flask provided the necessary tools to handle HTTP requests, manage sessions, and render HTML templates.

### NewsAPI
The application integrates with the NewsAPI service to fetch news articles and headlines. The API key is securely stored in the code, and the `newsapi` Python library is used to interact with the NewsAPI endpoints. The fetched data includes articles' URLs, sources, and other relevant information.

### Sentiment Analysis
Sentiment analysis is performed on the text content of each article using the Natural Language Toolkit (NLTK) library's SentimentIntensityAnalyzer. The sentiment scores are then processed to provide a percentage value, indicating the overall sentiment of each article. This information is used to generate sentiment scores for different news sources.

### Web Scraping
To extract text content from article URLs, the `find_text_in_url()` function uses the requests library for making HTTP requests and BeautifulSoup for HTML parsing. The function is designed to handle timeouts, retries, and excludes certain domains known to cause issues or provide irrelevant content.

> Note: the HTML parser makes no distinction between what kind of text is present in the webpage associated with the URL. All text is analyzed--even that from the navbar, other headlines, and other irrelevant data. What I was hoping for was that the weight from the article itself to the sentiment would overshadow the weight of irrelevant words. However, this was a sacrifice I made when deciding to use the NewsAPI servic. I prioritized the access to more sources at the cost of accuracy in the sentiment data.

### Session Management
Flask-Session is utilized for session management. It allows the application to store user-specific information across requests. I used it here to maintain a list of selected news sources that the user prefers.

## How it Works
The querying follows this rough outline:
1. When the user submits a query, get their preferences from their selected settings.
2. Using the information gathered from the settings, search for the query using the NewsAPI service's built in function.
3. The NewsAPI service will return a list of articles, their description, a snippet of their content, their URLs, etc. in JSON format that follow the parameters listed by the user
4. Go to each individual URL and find all the text within the website by parsing through it using the BeautifulSoup library to collect the text.
5. Within this text, use the VADER sentiment analysis to find a value that approximates how a news source feels, and scales that score to be within 0-100
6. If there is already a sentiment score for this news source, average the two existing sentiment scores
7. Repeat steps 4-6 for every article and then return the name of each source with its respective score
8. Render the html page with the appropriate template and variables

The top word counter follows this rough outline:
1. A request is made to the NewsAPI service and it returns the top headlines and articles from CNN, Fox News, and Reuters.
2. The NewsAPI service will return a list of articles, their description, a snippet of their content, their URLs, etc. in JSON format that are from CNN, Fox News, and Reuters
3. Go to each individual URL and find all the text within the website by parsing through it using the BeautifulSoup library to collect the text.
4. Append this text to a string until all articles have been scraped and appended.
5. Use a counter function to count the number of times a word that is not in the filtered word list appears in this long string, and then find the top 5 most common words.
6. Render the html page with the appropriate template and variables

For more information about VADER's documentation, please visit:
https://vadersentiment.readthedocs.io/en/latest/pages/about_the_scoring.html
and
https://vadersentiment.readthedocs.io/en/latest/pages/code_and_example.html

> Note: We only look at the compound score when determining scores for each source, and we scale it by doing (compound_score + 1) * 50.

## Design Decisions
I had some ideas for my project, and I attempted to go with a frosted glass look. I couldn't make it exactly as I had thought out in my head, but I think I did a pretty good job of approximating that look. I wanted the colors to kind of pop in the background, so I added some circles of different background and colors. Those circles also slightly "breathe" if you watch them closely. I really wanted to practice CSS animation in the website, so I added a lot of tiny little animations throughout the entirety of the website.

I initially only planned to have 3 news sources because of the effort it would take to manually scrape those pages, but I managed to find a service (NewsAPI) that does all that hard work for me. Because of that, it seemed like a great idea to allow the user to customize how they want to query the data by allowing them to change their sources and time frame.

I considered using Textblob as a sentiment analysis but after rigorous testing I only ever saw "Neutral" or "Somewhat negative" results, which meant that the Textblob service was not sensitive enough to specific words. I tried adding an optional "Deep Search"  feature that used a different analyzer than Textblob's default, but I decided it would be better if I changed to VADER from NLTK and then I saw all different types of results.

### During Testing
I noticed my testers were trying to access other parts of the page when searching something, which would lead them to accidentally interrupt the load process. So, I added a loading screen to stop them and also to help visualize the fact that the code is processing.

I noticed extremely long load times at some points. This was happening in the `find_text_in_url()` function, likely when I tried to connect to each page. I added a specified number of retries (3), and only gave each website 5 seconds to respond before I skipped them, which significantly reduced load times. Similarly, there were a few noticeable domains that caused problems frequently ("disneyparks.disney.go.com") or were irrelevant ("cnnespanol.cnn.com", "removed.com"). So, I made so no website went through these sources. URLs from IGN also seem to cause issues from time to time, but I have no precaution implemented for them except the standard 3 retries and 5 seconds.
