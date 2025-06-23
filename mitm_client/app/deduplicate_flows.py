import os
from collections import OrderedDict

from mitmproxy.http import HTTPFlow
from mitmproxy.io import FlowReader, FlowWriter


def _deduplicate_file(path: str):
    """
    Deduplicates flows in a single file.
    """
    collection: OrderedDict[tuple[str, str], HTTPFlow] = OrderedDict()
    rest = []
    with open(path, "rb") as f:
        reader = FlowReader(f)
        for flow in reader.stream():
            if isinstance(flow, HTTPFlow):
                key = (flow.request.method, flow.request.url)
                collection[key] = flow
            else:
                rest.append(flow)
    with open(path, "wb") as f:
        writer = FlowWriter(f)
        for flow in collection.values():
            writer.add(flow)
        for flow in rest:
            writer.add(flow)


def deduplicate_flows(path: str):
    """
    Deduplicates flows in the given path.
    If path is a file, deduplicates that file.
    If path is a directory, deduplicates all .mitm files in that directory.
    """
    if os.path.isdir(path):
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".mitm"):
                    _deduplicate_file(os.path.join(root, file))
    elif os.path.isfile(path):
        _deduplicate_file(path)
