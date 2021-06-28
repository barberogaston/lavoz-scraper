FROM python:3.9

WORKDIR /app

COPY . .

ENV TERM=vt100

RUN pip install --no-cache-dir -r requirements.txt

CMD ["/bin/bash", "-c", "python main.py"]
