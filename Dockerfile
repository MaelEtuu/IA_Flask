FROM python:3.10-slim

RUN pip install Flask
RUN pip install Flask Flask-SQLAlchemy Flask_Session
RUN pip install influxdb_flask
RUN pip install numpy
RUN pip install scikit-learn
RUN pip install pandas
RUN pip install tensorflow
RUN pip install matplotlib
RUN pip install flask opencv-python gdown numpy gunicorn
RUN apt-get update && apt-get install -y libgl1 libglib2.0-0 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . /app

EXPOSE 5007

CMD ["python", "app.py"]