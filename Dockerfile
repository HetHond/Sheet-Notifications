FROM python:3.11

WORKDIR /usr/src/sheet-notifications
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
CMD ["python", "-m", "src", "--service-account"] 