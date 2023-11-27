# Code partly from Thomas Nordlis "Dockerfile-eksempel"

# This is the Dockerfile for the Web Interface

FROM httpd:alpine
WORKDIR ./

# Enable CGI
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> conf/httpd.conf; \
    echo "AddHandler cgi-script .cgi"               >> conf/httpd.conf

# Let all requests be handled by interface.cgi
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/interface.cgi|' conf/httpd.conf

# Replace default cgi-bin directory to my new one
RUN sed -i 's|/usr/local/apache2/cgi-bin|/usr/lib/cgi-bin|g' conf/httpd.conf

# Install CURL
RUN apt-get update && apt-get install -y curl

COPY ./interface.cgi /usr/lib/cgi-bin/

EXPOSE 80
