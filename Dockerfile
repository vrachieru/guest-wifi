FROM python:3-alpine

MAINTAINER Victor Rachieru

WORKDIR /app
COPY . .

RUN apk --update --no-cache add openssh-client \
    && pip install -r requirements.txt

EXPOSE 80

CMD [ "python", "app.py" ]
