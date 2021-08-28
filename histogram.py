from re import T
from fastapi import FastAPI, Request
from prometheus_client import Histogram, start_http_server
import time

METRIC_PORT = 8181

app = FastAPI()

# METRIC
"""
Metric Structure : MetricType(name, hint, labels)
Example : 
  Counter('app_http_request_count_with_label', 'Total App HTTP Request With Labels', ['endpoint'])
"""

REQUEST_RESPOND_TIME = Histogram('app_http_respond_time', 'App Repond Time')
REQUEST_RESPOND_TIME_CUSTOM_BUCKETS = Histogram('app_http_respond_time_custom_bucket', 'App Repond Time Custom Bucket',buckets=[0.1,0.5,1,2,3,4,5])

@app.get('/')
def index(req: Request):
  metric_url = f'{req.url.scheme}://{req.url.hostname}:{METRIC_PORT}'
  return {
    "message": "Histogram Triggered",
    "urls": {
      "metric": f"{metric_url}"
    }
  }

# Basic
@app.middleware("http")
async def triggered_histogram(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    request_duration = time.time() - start_time
    REQUEST_RESPOND_TIME.observe(request_duration)
    REQUEST_RESPOND_TIME_CUSTOM_BUCKETS.observe(request_duration)
    return response


# Using Build in Function
# @app.middleware("http")
# @REQUEST_RESPOND_TIME.time()
# @REQUEST_RESPOND_TIME_CUSTOM_BUCKETS.time()
# async def triggered_histogram_with_buildin(request: Request, call_next):
#     time.sleep(4)
#     response = await call_next(request)
#     return response


@app.on_event('startup')
def startup_events():
  # start prometheus server / metrics
  start_http_server(port=METRIC_PORT)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, port=8282)