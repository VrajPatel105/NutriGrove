# Using fastapi for getting response and sending resopnses to the user
from fastapi import FASTAPI
from fastapi.responses import JSONResponse

app = FASTAPI()

@app.get('/recommendations')
def get_recommendations():
    