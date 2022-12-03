import json  # NOQA
import urllib  # NOQA

from puppy.http.utilities import pathsplit  # NOQA
from puppy.http.server.router import HTTPRouter, POST  # NOQA


def parse(request):
    # Create dictionary of parameters
    parameters = dict()

    # Add all parameters
    parameters.update(dict(parse_query(request)))
    parameters.update(dict(parse_content(request)))

    # Return parsed parameters
    return parameters


def parse_query(request):
    # Parse the query for parameters
    _, query, _ = pathsplit(request.location)

    # Make sure query is defined
    if not query:
        return

    # Split query by amp and loop over values
    for pair in query.split(b"&"):
        # Make sure the equals sign exists
        if b"=" not in pair:
            continue

        # Split by the sign
        name, value = pair.split(b"=", 1)
        name, value = name.strip(), value.strip()

        # Decode as url parameters
        name, value = urllib.unquote(name), urllib.unquote(value)

        # Yield the name and the value
        yield name, value


def parse_content(request):
    # Make sure the request is a POST
    if request.method != POST:
        return

    # Parse the content as JSON
    for name, value in json.loads(request.content).items():
        yield name, value


class Router(HTTPRouter):
    def attach(self, location, *methods):
        # Create function wrapper
        def wrapper(function):
            # Create a new handler for a function
            def handler(request):
                # Create dict of parameters
                parameters = parse(request)

                try:
                    # Try calling the function
                    result = function(request, **parameters)

                    # Return a success string
                    return json.dumps({"success": True, "result": result})
                except BaseException as exception:
                    # Return a failure string
                    return json.dumps({"success": False, "result": str(exception)})

            # Add API route to routes
            self.add(b"/api/%s" % location.lstrip(b"/"), handler, *methods)

            # Return the original function
            return function

        # Return the wrapper
        return wrapper


def create_router(indexes=["index.htm", "index.html"]):
    # Create router from parameters
    router = Router()
    router.static("../frontend", indexes=indexes)

    # Return the created router
    return router


# Create default router
router = create_router()
