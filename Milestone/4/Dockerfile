# Code partly from Thomas Nordlis "Dockerfile-eksempel"

FROM httpd:alpine
WORKDIR ./Milestone/4/tmp/

# Install SQLite3
RUN apk add sqlite

# Enable CGI
RUN echo "LoadModule cgi_module modules/mod_cgi.so" >> conf/httpd.conf; \
    echo "AddHandler cgi-script .cgi"               >> conf/httpd.conf

# Lar alle forespørsler håndteres av index.cgi
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/rest.cgi|' conf/httpd.conf

COPY ./Milestone/3/rest.cgi /Milestone/3/DiktDatabase.db

CMD ["rest.cgi"]
