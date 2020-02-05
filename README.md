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

The overall sentiment score is a result of ensembling of these 3 model predictions.

##### Flask web application
Simple Flask web application is currently hosted at <a href="http://datahappy.pythonanywhere.com">http://datahappy.pythonanywhere.com</a>, source code can be found in this location <a href="https://github.com/datahappy1/czech_language_sentiment_analyzer/tree/master/flask_webapp">/flask_webapp/</a>.
This application backend is written in Python using the `Flask` framework and `Bootstrap` for the templates styling. This app also provides the users with a simple API. 