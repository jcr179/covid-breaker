
1. Download dataset https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge to this folder.
It will have several directories mentioned in 'parse_paper_jsons.py' filled with papers. 
This data is omitted from this commit/repo for space.

2. Run 'parse_paper_jsons.py' - this creates the trimmed_papers directory with all papers with trimmed fields
in it, all as their own .json file.

3. Start at least 2 instances of elasticsearch. For the 2nd instance, specify a data path and log path:
https://www.elastic.co/guide/en/elasticsearch/reference/current/getting-started-install.html

4. Run 'indexer.go' to bulk index batches of the documents from trimmed_papers at a time.

(Done)

N. 'trimmed_to_single.py' is a script that takes the .jsons in trimmed_papers and puts them all in a 
raw json file ready to be directly bulk indexed with elasticsearch via curl, but it seems to be
too big for memory to do all at once, hence the approach taken with indexer.go - but I will keep it
in case it becomes useful later.

N2. 'paper.json' is a single paper formatted to be ready for bulk indexing via curl, for testing only.