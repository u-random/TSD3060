# REST API Dockerfile

FROM cgi-image:base
WORKDIR ./

# ROUTE traffic
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/rest.cgi|' conf/httpd.conf

# INSTALL SQLite3
RUN apk add sqlite

# COPY over necessary files to cgi-bin
COPY ./rest.cgi ./DiktDatabase.db /usr/local/apache2/cgi-bin/

RUN busybox chmod 666 /usr/local/apache2/cgi-bin/DiktDatabase.db

# Change owner to www-data/dockremap of Directory and Database
#RUN busybox chown dockremap  /usr/local/apache2/cgi-bin \
#                            /usr/local/apache2/cgi-bin/DiktDatabase.db
