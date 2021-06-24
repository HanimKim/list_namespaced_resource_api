FROM python:3.8.6

RUN addgroup --system -gid 1000 app && adduser --system -uid 1000 -gid 1000 app

WORKDIR /app
RUN chmod -R 755 /app
RUN chown -R app:app /app

COPY pkg/pip-requirement.txt ./
RUN pip install -r pip-requirement.txt --ignore-installed

COPY . /app

USER app
EXPOSE 8000
CMD ["sh", "start"]

