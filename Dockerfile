FROM ghcr.io/gchux/cloud-run-ssh:lite-root

ENV SSH_USER=moon
ENV SSH_PASS=moon
ENV PASSWORD_ACCESS=true
ENV SSH_AUTO_LOGIN=false

# مهم للتونل
ENV WEBSSH_PORT=8080
EXPOSE 8080