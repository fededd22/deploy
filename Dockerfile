FROM ghcr.io/gchux/cloud-run-ssh:lite-root

# Configuration utilisateur moon / password moon
ENV SSH_USER=moon
ENV SSH_PASS=moon
ENV PASSWORD_ACCESS=true
ENV SSH_AUTO_LOGIN=true
ENV WEBSSH_PORT=8080

# Port attendu par Cloud Run
EXPOSE 8080