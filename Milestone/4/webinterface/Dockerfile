# WEB INTERFACE Dockerfile

FROM cgi-image:base
WORKDIR ./

# ROUTE traffic
RUN sed -i 's|ScriptAlias .*|ScriptAliasMatch .* /usr/local/apache2/cgi-bin/interface.cgi|' conf/httpd.conf

# COPY over necessary files to cgi-bin
COPY ./interface.cgi ./index.html /usr/local/apache2/cgi-bin/
