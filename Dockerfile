FROM python

RUN pip install flask flask_socketio
COPY ./ ./
ENTRYPOINT ["python", "Main.py"]
