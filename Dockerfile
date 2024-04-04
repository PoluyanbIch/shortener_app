FROM python:3.11-slim

COPY . .

RUN pip install -r requirements.txt

CMD uvicorn main:app --host 0.0.0.0 --port 80

#docker build . --tag shortener_app
#docker run -p 80:80 shortener_app
#go to localhost in your web browser