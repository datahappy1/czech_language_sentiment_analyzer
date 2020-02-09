#### CZEch SentimenT analyzER "czester"
##### Data Collection
56k Czech movie reviews were collected using the <a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/blob/master/data_preparation/data_collector_movie_review_scraper.py">/data_preparation/data_collector_movie_review_scraper.py</a>
multithreaded HTML scraping module. To have the data balanced with the same amount of negative and positive reviews, the
final dataset had to be reduced to 14k positive and 14k negative reviews.
 This dataset was scrubbed agains a collection of Czech stopwords. 

##### Models
From `Scikit-Learn` Python library, `Naive Bayes`, `Logistic regression` and `Support Vector Machine` models were used
for training and testing data for text sentiment analysis.
The scripts for training and testing are located here: 
<ul>
<li><a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/tree/master/ml_models/logistic_regression">/ml_models/logistic_regression</a></li>
<li><a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/tree/master/ml_models/naive_bayes">/ml_models/naive_bayes</a></li>
<li><a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/tree/master/ml_models/support_vector_machine">/ml_models/support_vector_machine</a></li>
</ul>

The overall sentiment score for the specified text input is calculated as a weighted average based on the precision score accuracy of these 3 model predictions.

##### Flask web application
Simple Flask web application is currently hosted at <a href="http://datahappy.pythonanywhere.com">http://czester.pythonanywhere.com</a>, source code can be found in this location <a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/tree/master/flask_webapp">/flask_webapp/</a>.
This application backend is written in Python using the `Flask` framework and `Bootstrap` for the templates styling. This app also provides the users with a simple API. The stats module is an integration of `Charts.js` and `Flask` with the statistics data persistence layer being `sqlite3`.

##### Useful links
<ul>
    <li><a href="https://scikit-learn.org/stable/tutorial/text_analytics/working_with_text_data.html">Scikit-Learn working with text data</a></li>
    <li><a href="https://www.pluralsight.com/guides/ensemble-modeling-scikit-learn">Ensembling with Scikit-Learn</a></li>
    <li><a href="https://www.chartjs.org/docs/latest/charts/">Charts.js homepage</a></li>
</ul>

##### How to run this Flask App from local environment
<ul>
    <li>create and activate a virtual or pipenv environment</li>
    <li>pip3 install the requirements from requirements.txt</li>
    <li>set the working directory for instance to the path where you cloned this repo (Make sure it's the path where the Heroku Procfile file is located)</li>
</ul>

##### TODOs
<ul>
    <li>Czech word lemmatizer / stemmatizer module</li>
    <li>Scrape also some product reviews</li>
    <li>Remove reviews written in Slovak language</li>
    <li>Ensembling instead of weighted model precision average for overall sentiment</li>
    <li>Redis could replace Sqlite3</li>
</ul>