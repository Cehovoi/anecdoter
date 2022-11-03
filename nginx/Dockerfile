FROM nginx:1.19-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/conf.d
COPY /etc/letsencrypt/live/anecdoter.su/fullchain.pem /etc/ssl/fullchain.pem
COPY /etc/letsencrypt/live/anecdoter.su/privkey.pem /etc/ssl/privkey.pem
