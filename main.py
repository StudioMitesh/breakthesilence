from flask import Flask
from firebase_functions import https_fn
import app as app

@https_fn.on_request
def flasking(request):
    return app.app(request)
