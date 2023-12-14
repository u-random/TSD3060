# REST API Dockerfile

# Milestone 4.5: Containernes Dockerfiler skal være basert på egendefinert bilde
FROM cgi-image:base
WORKDIR ./

# INSTALL SQLite3
RUN apk add sqlite

# COPY over necessary files to cgi-bin
COPY ./index.cgi ./DiktDatabase.db /usr/local/apache2/cgi-bin/

# Change owner to www-data of Directory and Database
RUN busybox chown www-data  /usr/local/apache2/cgi-bin \
                            /usr/local/apache2/cgi-bin/DiktDatabase.db && \
    busybox chmod 666       /usr/local/apache2/cgi-bin/DiktDatabase.db
