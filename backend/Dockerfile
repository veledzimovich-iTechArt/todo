FROM python

ENV PYTHONUNBUFFERED=1

WORKDIR /backend
COPY requirements.txt /backend/
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
