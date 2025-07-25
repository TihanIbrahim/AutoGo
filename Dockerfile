FROM python:3.13.5

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends libfreetype6=2.12.1+dfsg-5+deb12u4 libfreetype6-dev=2.12.1+dfsg-5+deb12u4 && \
    rm -rf /var/lib/apt/lists/*



WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]