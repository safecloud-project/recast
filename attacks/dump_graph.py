#! /usr/bin/env python
"""
A script that dumps the entanglement graph (in the form of a dict) from playcloud.
"""
import json
import pickle
import requests
import os

def fetch_entanglement_graph(host="127.0.0.1", port=3000, path="/dict"):
    """
    Fetches the entanglement graph from a running instance of playcloud.
    Args:
        host(str, optional): Host of the playcloud instance
        port(int, optional): Port number of the listening playcloud instance
        path(str, optional): Path of the endpoint on the playcloud server that dumps the graph
    Returns:
        dict: The entanglement graph
    """
    url = "http://{:s}:{:d}{:s}".format(host, port, path)
    req = requests.get(url)
    assert req.status_code == 200
    graph = json.loads(req.text)
    return graph


def dump_entanglement_graph(graph):
    """
    Dumps the graph to a file
    Args:
        graph(dict): The entanglement graph
    Returns:
        str: The path to the dictionary
    """
    full_path = os.path.join("./dictionaries", "dict.pickle")
    with open(full_path, "wb") as handle:
         pickle.dump(graph, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return full_path
     

if __name__ == "__main__":
    graph =  fetch_entanglement_graph()
    print dump_entanglement_graph(graph)
