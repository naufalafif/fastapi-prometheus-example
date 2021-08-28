from fastapi import FastAPI, Request
from prometheus_client import start_http_server, Counter

METRIC_PORT = 8181

app = FastAPI()

# METRIC
"""
Metric Structure : MetricType(name, hint, labels)
Example : 
  Counter('app_http_request_count_with_label', 'Total App HTTP Request With Labels', ['endpoint'])
"""

REQUEST_TOTAL = Counter('app_http_request_count', 'Total App HTTP Request')
REQUEST_TOTAL_WITH_LABEL = Counter('app_http_request_count_with_label', 'Total App HTTP Request With Labels', ['endpoint'])

@app.get('/')
def index(req: Request):
  metric_url = f'{req.url.scheme}://{req.url.hostname}:{METRIC_PORT}'
  base_url = f'{req.url.scheme}://{req.url.hostname}:{req.url.port}'
  return {
    "message": "Counter Triggered",
    "urls": {
      "urlb": f"{base_url}/b",
      "urlc": f"{base_url}/c",
      "metric": f"{metric_url}"
    }
  }

@app.get('/a')
def urlb():
  return "Counter Triggered"


@app.get('/b')
def urlb():
  return "Counter Triggered"

@app.middleware("http")
async def triggered_counter(request: Request, call_next):
    REQUEST_TOTAL.inc()
    REQUEST_TOTAL_WITH_LABEL.labels(request.url.path).inc()
    response = await call_next(request)
    return response

@app.on_event('startup')
def startup_events():
  start_http_server(port=METRIC_PORT)


if __name__ == '__main__':
  import uvicorn
  uvicorn.run(app, port=8282)