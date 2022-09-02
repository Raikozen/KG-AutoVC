FROM python:3.10

# Install dependencies
ENV PYTHONUNBUFFERED=1

RUN mkdir /kgavc

WORKDIR /kgavc

ADD . /kgavc/

RUN pip install -r requirements.txt

# Run the application
CMD ["python", "./start-bot.py"]