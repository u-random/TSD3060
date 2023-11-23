#!/bin/bash

# Use HTML forms for the CRUD Operation

# Interface with several servers on local host, MP 2, MP 3.
# Use HTTP GET, POST, PUT, DELETE to MP 3 server for all data

# Use URI as definition:
# /dikt or /dikt/ for all dikt
# /dikt/1 for single dikt with HTML form below to edit, if logged in

# On main /dikt page, there should be a login button at the top if not logged in.
# Logged in status, username and logout button if logged in

# Below should be the full dikt database list

# Below that should be the ADD dikt HTML FORM

# To delete, there are alternatives:
# 1. Delete button beside the dikt entries on main page
# 2. Delete button on dikt/id page, not visible from main page
# 3. Delete text field, where ID can be specified, semicolon seperated.


start
    Har vi session cookie?
      Nei: vis login knapp ->
        1. hente alle dikt -> all()
        2. hente ut ett bestemt dikt (gitt diktID)
      Ja: vis logout knapp ->
        1. hente alle dikt,
        2. hente ut ett bestemt dikt (gitt diktID)
        3. legge til nytt dikt,
        4. endre egne dikt,
        5. slette eget dikt (gitt diktID) og
        6. slette alle egne dikt
      

template.html kjør

sed 's/@content@/'"$content"'/'  template.html


alle() {

# Content
if [ loggedin ]
then
cat << EOF
    <button style="float:right;">Login</button>
EOF
else
cat << EOF
    <button  style="float:right;">Logout</button>
EOF
if

sed 's/@content@/$content/' template.html

hent alle dikt from curl -i localhost:8280/dikt xml-format:

<dikt>
<id>1</id><tittel>Skrønebok</tittel><epost>demo@demomail.com</epost>
<id>2</id><tittel>Skrønebok 2. Vittighetenes tilbakekomst!</tittel><epost>demo@demomail.com</epost>
<id>3</id><tittel>Skrønebok 3. Atter en vits!</tittel><epost>demo@demomail.com</epost>
</dikt>

Bruk awk og spørr chatgpt om transformer til HTML:

<style>
 table {width:100%; text-align:left;}
table, th, td {
  border: 1px solid black;
  border-collapse: collapse;
}
td,th { padding: 5px 2px 5px 5px; }
</style>
<table>
    <tr>
        <th style="width:5%; text-align:center">#</th>
        <th>Dikt</th>
    </tr>
    <tr>
        <td style="text-align:center">1</td>
        <td>
            <a href="/container2/dikt/1">Skrønebok</a>
        </td>
    </tr>
    <tr>
        <td style="text-align:center">2</td>
        <td>
            <a href="/container2/dikt/2">Skrønebok 2. Vittighetenes tilbakekomst!</a>
        </td>
    </tr>
    <tr>
        <td style="text-align:center">3</td>
        <td>
            <a href="/container2/dikt/3">Skrønebok</a>
        </td>
    </tr>
</table>


#

do_login() {

curl -c ~/cookies.txt -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d '<login><email>demo@demomail.com</email><password>admin</password></login>' http://localhost:8280/login


read HTTP_BODY

cat << EOF
<!doctype html>
<html>
    <head>
        <meta charset='utf-8'>
        <title>LOGIN</title>
    </head>
    <body>
        <form action="http://container3/login" method='post'>
            <label for="username">Username:</label><br>
            <input type="text" id="username" name="username"><br>
            <label for="password">Password:</label><br>
            <input type="password" id="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
        <pre>
        Debug info om HTTP-forespørsel:
        -------------------------
        Kroppens innhold: $HTTP_BODY
        Metode:           $REQUEST_METHOD
        Kroppens lengde:  $CONTENT_LENGTH
        </pre>
    </body>
</html>
EOF
}

# MARK: - GET DIKT, ONE OR ALL
# Function to get a dikt from ID and return proper XML
get_dikt() {
    # Extract diktID from array variable Bash_rematch with result of regex match
    local diktID=${BASH_REMATCH[2]}
    # Fetch the dikt with DiktID
    if [[ -n $diktID ]]; then
        # Validate that the variable is numeric
        if [[ $diktID =~ ^[0-9]+$ ]]; then
            local xml_response=$(curl -i localhost:8280/dikt/$diktID)
            dikt_from_xml "$xml_response"
        # Prints errormessage if diktID is not a number
        else
            write_body "<error>Invalid Dikt ID. It has to be a number.</error>"
        fi
    # If no ID specified, send all dikt
    else
        local xml_response=$(curl -i localhost:8280/dikt)
        dikt_from_xml "$xml_response"
    fi
}


# MARK: - To print dikts, used in get_dikt
dikt_from_xml() {
# Execute curl and store the response
xml_response=$(curl -i localhost:8280/dikt)

# Use the response in an awk script
echo "$xml_response" | awk '
BEGIN {
    print "<table>";
    print "    <tr>";
    print "        <th style=\"width:5%; text-align:center\">#</th>";
    print "        <th>Dikt</th>";
    print "    </tr>";
}

/<id>/ {
    gsub(/<[^>]*>/, ""); # Remove XML tags
    id = $0; # Store the ID
    getline; # Get the next line (tittel)
    gsub(/<[^>]*>/, ""); # Remove XML tags
    tittel = $0; # Store the title
    print "    <tr>";
    print "        <td style=\"text-align:center\">" id "</td>";
    print "        <td>";
    print "            <a href=\"/container2/dikt/" id "\">" tittel "</a>";
    print "        </td>";
    print "    </tr>";
}

END {
    print "</table>";
}'
}



echo "Content-type: text/html"
echo ""

# Method detection (rudimentary)
METHOD=$(echo $REQUEST_METHOD)
URI=$(echo $REQUEST_URI)

# Basic Routing
case $URI in
    "/dikt"|"dikt/")
        # Handle main page
        if [ "$METHOD" = "GET" ]; then
            # Display list of dikts
            # Use curl to get data from API and parse it to display
        fi
        ;;
    "/dikt/[0-9]+" )
        # Handle individual dikt
        if [ "$METHOD" = "GET" ]; then
            # Display individual dikt
            # Use curl to get data from API and parse it
        fi
        ;;
    *)
        # Default case
        echo "<html><body><h1>404 Not Found</h1></body></html>"
        ;;
esac

# Further logic for form processing, authentication, etc. goes here.


# MARK: - CASE statement
# REST API logic
case $METHOD in
    # MARK: - HTTP GET request. Matches SQL: SELECT
    GET)
        # REGEX for URI to match: /dikt, /dikt/ and /dikt/{id} where {id} is a number.
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?/?$ ]]; then
            # Run my function to get dikts
            get_dikt
        else
            write_body "<error>Invalid request. Use /dikt for all dikts or /dikt/{id} for a specific dikt.</error>"
        fi
        ;;
    
    
    # MARK: - HTTP POST request. Matches SQL: INSERT
    POST)
        read -r HTTP_BODY
        case "$URI" in
            /login)
                # Run my log in function
                do_login
                ;;

            /logout)
                # Run my log out function
                do_logout
                ;;
    
            /dikt)
                # Run my add new dikt function
                add_dikt
                ;;
        esac
        ;;


    # MARK: - HTTP PUT request. Matches SQL: UPDATE
    PUT)
        read -r HTTP_BODY
        # REGEX for URI to match: only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
            # Run my edit function
            edit_dikt_from_id
        else
            write_body "<error>Unable to update. {id} for dikt/{id} has to be a number.</error>"
        fi
        ;;


    # MARK: - HTTP DELETE request. Matches SQL: DELETE
    DELETE)
        read -r HTTP_BODY
        # Should match only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
            # Run my delete function
            delete_dikt_from_id
        else
            echo "<error>Cannot delete all dikts at once. {id} for dikt/{id} has to be a number.</error>"
        fi
        ;;
esac
