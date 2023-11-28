# WEB INTERFACE Dockerfile

FROM cgi-image:base
WORKDIR ./

# ROUTE traffic
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/lib/cgi-bin/interface.cgi|' conf/httpd.conf

# COPY over necessary files to cgi-bin
COPY ./interface.cgi /usr/lib/cgi-bin/
