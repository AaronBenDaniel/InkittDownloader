FROM node:20

WORKDIR /build
COPY src/frontend/package*.json .
RUN rm -rf node_modules
RUN rm -rf build
RUN npm install
COPY src/frontend/. .
RUN npm run build
# Thanks https://stackoverflow.com/q/76988450

FROM python:3.10-slim

WORKDIR /app
COPY src/api/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY --from=0 /build/build /app/build
# COPY src/api/src/.env .env
COPY src/api/src .
COPY ./inkitt_credentials .

EXPOSE 80
# ENV PORT=80

CMD [ "python3", "main.py"]

