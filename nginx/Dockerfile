FROM nginx:1.27-alpine

RUN apk add --no-cache openssl

COPY nginx.conf /etc/nginx/nginx.conf
COPY docker-entrypoint.sh /usr/local/bin/sams-nginx-entrypoint
RUN chmod +x /usr/local/bin/sams-nginx-entrypoint

ENTRYPOINT ["/usr/local/bin/sams-nginx-entrypoint"]
