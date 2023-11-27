#!/bin/bash

# TODO : REMOVE
# Small function to write header
write_headers() {
echo "Content-type: text/xml; charset=UTF-8"
echo ""
}


# MARK: - LOGIN OK
do_login() {
    # Use awk to parse the email and password values
    local email_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "email") {print $(i+1); break}}')
    local password_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "password") {print $(i+1); break}}')
    
    #TODO URL decode email and password
    local email=$(perl -MURI::Escape -e 'print URI::Escape::uri_unescape($ARGV[0])' "$email_encoded")
    local password=$(perl -MURI::Escape -e 'print URI::Escape::uri_unescape($ARGV[0])' "$password_encoded")

    # Login and Write return to browser
    write_headers
    curl -c ~/cookies.txt -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<login><email>$email</email><password>$password</password></login>" restapi/login
}


# MARK: - LOGOUT OK
do_logout() {
    # Logout and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" restapi/logout
}


# MARK: - GET DIKTS V
get_dikt() {
# Parse diktID from HTML form
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')

# Is DiktID defined
if [[ -n $diktID ]]; then
    # Validate that the variable is numeric
    if [[ $diktID =~ ^[0-9]+$ ]]; then
        write_headers
        curl "restapi/dikt/$diktID"
    fi
# If no ID specified, request all dikt
else
    write_headers
    curl restapi/dikt
fi
}


# MARK: - ADD NEW DIKT V
add_dikt() {
    # Parse new title
    local title_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')
    # Decode title
    local title=$(perl -MURI::Escape -e 'print URI::Escape::uri_unescape($ARGV[0])' "$title_encoded")
    # Add dikt and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X POST -H "Content-Type: text/xml" -d "<title>$title</title>" restapi/dikt
}


# MARK: - EDIT DIKT V
edit_dikt_from_id() {
    # Parse new title
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    local title_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')
    # Decode title
    local title=$(perl -MURI::Escape -e 'print URI::Escape::uri_unescape($ARGV[0])' "$title_encoded")

    # Edit dikt and Write return to browser
    write_headers
    curl -b ~/cookies.txt -X PUT -H "Content-Type: text/xml" -d "<dikt><title>$title</title></dikt>" "restapi/dikt/$diktID"
}


# MARK: - DELETE DIKT V
delete_dikt_from_id() {
    # Parse diktID
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    # Delete dikt and Write reply to browser
    write_headers
    curl -b ~/cookies.txt -X DELETE "restapi/dikt/$diktID"
}


# GET info from headers
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')


# MARK: - CASE statement OK
read -r HTTP_BODY
case $METHOD in
    GET)
        case "$URI" in
            /logout)
                # Run my log out function
                do_logout
                ;;
        esac
        ;;
    POST)
        case "$URI" in
            /login)
                # Run my log in function
                do_login
                ;;

            /logout)
                # Run my log out function
                do_logout
                ;;
    
            /dikt/get)
                # Run my function to get dikts
                get_dikt
                ;;
            /dikt/add)
                # Run my add new dikt function
                add_dikt
                ;;

            /dikt/edit)
                # Run my edit function
                edit_dikt_from_id
                ;;

            /dikt/delete)
                # Run my delete function
                delete_dikt_from_id
                ;;

                
        esac
        ;;

esac
