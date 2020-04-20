Covid-Breaker goal: Intuitive, responsive, highly available COVID-19 research database for searching. 

Data source (cases): https://github.com/CSSEGISandData/COVID-19
Data source (research): https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge

Currently: ETL logic done (get dataset, transform, load to elasticsearch index), need tests and extract script
Milestone 1: Basic interface done and hosted.
Milestone 2: Implement updating database automatically as the data source updates.
Milestone 3: Implement redis for caching common searches.
Milestone 4: Release.
Milestone 5: Include analytics for users to view.
