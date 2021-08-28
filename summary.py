from fastapi import FastAPI, Request
from prometheus_client import Summary, start_http_server
import time

METRIC_PORT = 8181

app = FastAPI()

# METRIC
"""
Metric Structure : MetricType(name, hint, labels)
Example : 
  Counter('app_http_request_count_with_label', 'Total App HTTP Request With Labels', ['endpoint'])
"""

REQUEST_RESPOND_TIME = Summary('app_http_respond_time', 'App Repond Time')

@app.get('/')
def index(req: Request):
  metric_url = f'{req.url.scheme}://{req.url.hostname}:{METRIC_PORT}'
  return {
    "message": "Summary Triggered",
    "urls": {
      "metric": f"{metric_url}"
    }
  }

# Basic
@app.middleware("http")
async def triggered_summary(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    request_duration = time.time() - start_time
    REQUEST_RESPOND_TIME.observe(request_duration)
    return response


# Using Build in Function
# @app.middleware("http")
# @REQUEST_RESPOND_TIME.time()
# async def triggered_summary_with_buildin(request: Request, call_next):
#     response = await call_next(request)
#     return response


@app.on_event('startup')
def startup_events():
  # start prometheus server / metrics
  start_http_server(port=METRIC_PORT)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, port=8282)