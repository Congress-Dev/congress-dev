FROM debian:jessie

RUN apt-get update && apt-get install -y nginx \
                        ca-certificates \
                        gettext-base
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

EXPOSE 80 443

CMD ["/usr/sbin/nginx", "-g", "daemon off;"]
