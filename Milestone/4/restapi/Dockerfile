# Code partly from Thomas Nordlis "Dockerfile-eksempel"

# This is the Dockerfile for the REST API

FROM httpd:alpine
WORKDIR ./

# Install SQLite3
RUN apk add sqlite

# Enable CGI
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> conf/httpd.conf; \
    echo "AddHandler cgi-script .cgi"               >> conf/httpd.conf
    
# Let all requests be handled by interface.cgi
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/rest.cgi|' conf/httpd.conf

# Replace default cgi-bin directory to my new one
RUN sed -i 's|/usr/local/apache2/cgi-bin|/usr/lib/cgi-bin|g' conf/httpd.conf

# Change owner to www-data in cgi bin
RUN /usr/bin/chown www-data /usr/lib/cgi-bin


# Install CURL
RUN apk --no-cache add curl

# Install bash
RUN apk add --no-cache bash

# Install XMLLINT needed for my xml request parsing
RUN apk add --no-cache libxml2-utils

# Install Utilities, including uuidgen
RUN apk update && apk add util-linux

COPY ./rest.cgi /usr/lib/cgi-bin/
COPY ./DiktDatabase.db /usr/lib/cgi-bin/

EXPOSE 80
