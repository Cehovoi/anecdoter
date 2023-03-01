FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY .ssl/$CERT ssl/$CERT
COPY .ssl/$KEY ssl/$KEY
COPY nginx.conf /etc/nginx/conf.d

