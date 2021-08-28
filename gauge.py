from fastapi import FastAPI, Request
from prometheus_client import Gauge, start_http_server
import time

METRIC_PORT = 8181

app = FastAPI()

# METRIC
"""
Metric Structure : MetricType(name, hint, labels)
Example : 
  Counter('app_http_request_count_with_label', 'Total App HTTP Request With Labels', ['endpoint'])
"""

REQUEST_INPROGRESS = Gauge('app_http_request_inprogress', 'Current In Progress App HTTP Request')
REQUEST_LAST_SERVED = Gauge('app_http_request_lastserved', 'Last Served HTTP Request')

@app.get('/')
def index(req: Request):
  metric_url = f'{req.url.scheme}://{req.url.hostname}:{METRIC_PORT}'
  return {
    "message": "Gauge Triggered",
    "urls": {
      "metric": f"{metric_url}"
    }
  }

# Basic
@app.middleware("http")
@REQUEST_INPROGRESS.track_inprogress()
async def triggered_gauge(request: Request, call_next):
    REQUEST_INPROGRESS.inc()
    response = await call_next(request)
    REQUEST_INPROGRESS.dec()
    REQUEST_LAST_SERVED.set(time.time())
    return response

# Using Build in Function
# @app.middleware("http")
# @REQUEST_INPROGRESS.track_inprogress()
# async def triggered_gauge_with_buildin(request: Request, call_next):
#     response = await call_next(request)
#     REQUEST_LAST_SERVED.set_to_current_time()
#     return response

@app.on_event('startup')
def startup_events():
  # start prometheus server / metrics
  start_http_server(port=METRIC_PORT)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, port=8282)