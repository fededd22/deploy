FROM ghcr.io/gchux/cloud-run-ssh:full-root

# إعدادات SSH
ENV SSH_USER=moon
ENV SSH_PASS=moon
ENV PASSWORD_ACCESS=true
ENV SSH_AUTO_LOGIN=false

# إعدادات WebSocket + HTTP Custom
ENV WEBSSH_PORT=8080
ENV PORT=8080

# Nginx config لدعم HTTP Custom بشكل أفضل
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080