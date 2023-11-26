# Code partly from Thomas Nordlis "Dockerfile-eksempel"

# This is the Dockerfile for the Web Interface

FROM httpd:alpine
WORKDIR ./

# Enable CGI
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> conf/httpd.conf; \
    echo "AddHandler cgi-script .cgi"               >> conf/httpd.conf

# Lar alle forespørsler håndteres av index.cgi
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/interface.cgi|' conf/httpd.conf

COPY ./interface.cgi /usr/lib/cgi-bin/
