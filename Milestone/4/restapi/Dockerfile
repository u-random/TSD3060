# Code partly from Thomas Nordlis "Dockerfile-eksempel"

# This is the Dockerfile for the REST API

FROM httpd:alpine
WORKDIR ./

# Install SQLite3
RUN apk add sqlite

# Enable CGI
RUN mkdir -p /etc/apache2 && \
    echo "LoadModule cgi_module modules/mod_cgi.so" >> /etc/apache2/httpd.conf; \
    echo "AddHandler cgi-script .cgi"               >> /etc/apache2/httpd.conf

# Lar alle forespørsler håndteres av index.cgi
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/rest.cgi|' /etc/apache2/httpd.conf

COPY ./rest.cgi /usr/lib/cgi-bin/
COPY ./DiktDatabase.db /usr/lib/cgi-bin/

EXPOSE 80
