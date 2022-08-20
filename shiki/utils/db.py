from pymongo.mongo_client import MongoClient


def connect():
    return MongoClient('127.0.0.1', 27017)


def insert_document(collection, data):
    """
    Function to insert a document into a collection and
    return the document's id.
    """
    return collection.insert_one(data).inserted_id


def find_document(collection, elements, multiple=False):
    """
    Function to retrieve single or multiple documents from a provided
    Collection using a dictionary containing a document's elements.
    """
    if multiple:
        results = collection.find(elements)
        return [r for r in results]
    else:
        return collection.find_one(elements)


def update_document(collection, query_elements, new_values):
    """ Function to update a single document in a collection."""
    collection.update_one(query_elements, {'$set': new_values})


def delete_document(collection, query):
    """ Function to delete a single document from a collection."""
    collection.delete_one(query)
