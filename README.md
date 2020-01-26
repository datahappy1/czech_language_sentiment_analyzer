# czech_language_sentiment_analyzer

## 1) Data Collection
56k Czech movie reviews were collected using the `/czech_language_sentiment_analyzer/data_preparation/data_collector_movie_review_scraper.py`
multithreaded HTML scraping module. To have the data balanced with the same amount of negative and positive reviews, the
final dataset had to be reduced to 14k positive and 14k negative reviews.
 This dataset was scrubbed agains a collection of Czech stopwords. 

## 2) Models
From Scikit-Learn Python library, Naive Bayes and Logistic regression models were used
for training and testing data for text sentiment analysis.
The scripts for training and testing are located here `/czech_language_sentiment_analyzer/ml_models/logistic_regression` and `/czech_language_sentiment_analyzer/ml_models/naive_bayes` 

## 3) Flask web application
Simple Flask web application is currently hosted at `http://datahappy.pythonanywhere.com` , source code can be found in this location `/czech_language_sentiment_analyzer/flask_webapp/`
This app is pure `Flask` and `bootstrap` for the templates styling. This app also provides the users with a simple API. 