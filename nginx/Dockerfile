FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY .ssl/chain.pem ssl/chain.pem
COPY .ssl/privkey.pem  ssl/privkey.pem
COPY .ssl/cert.pem ssl/cert.pem
COPY .ssl/fullchain.pem ssl/fullchain.pem
COPY nginx.conf /etc/nginx/conf.d

