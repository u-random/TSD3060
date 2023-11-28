# REST API Dockerfile

FROM cgi-image:base
WORKDIR ./

# ROUTE traffic
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/rest.cgi|' conf/httpd.conf

# INSTALL SQLite3
RUN apk add sqlite

# COPY over necessary files to cgi-bin
COPY ./rest.cgi ./DiktDatabase.db /usr/lib/cgi-bin/

# Change owner to www-data of Directory and Database
RUN busybox chown www-data  /usr/lib/cgi-bin \
                            /usr/lib/cgi-bin/DiktDatabase.db

#
RUN apk add shadow

RUN deluser xfs
RUN set -x; \
    deluser www-data && \
    delgroup www-data && \
    addgroup -g 33 -S www-data && \
    adduser -u 33 -D -S -G www-data www-data
