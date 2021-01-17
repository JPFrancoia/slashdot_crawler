# Slashdot crawler

This is a simple crawler for Slashdot. It collects information about each
article, and dump it into a MongoDB database. Information collected are:

- title
- url
- content of the article (raw HTML)
- datetime of the article

## MongoDB in Docker

Create a MongoDB server via Docker:

```console
docker run -d -p 27017:27017 --name mongo_slashdot mongo
```

## DB dump

Once the crawling is complete, you can dump the DB like this:

```console
mongodump --db=slashdot_db
```
