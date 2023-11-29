#!/bin/bash

# Global Varables
#cookie_file=""

build_html() {
  cat <<EOF > login-status.html
<!DOCTYPE html>
<html>
<head>
    <title>Login Status</title>
</head>
<body>
    <p>Status: [LOGIN_STATUS]</p>
</body>
</html>
EOF
}



# MARK: - LOGIN OK
do_login() {
    # Use awk to parse the email and password values
    local email_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "email") {print $(i+1); break}}')
    local password_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "password") {print $(i+1); break}}')
    
    #TODO URL decode email and password
    local email=$(echo "$email_encoded" | sed 's/%/\\x/g' | xargs -0 printf "%b")
    local password=$(echo "$password_encoded" | sed 's/%/\\x/g' | xargs -0 printf "%b")

    # Changes non alphanumeric to underscore
    local sanitized_email=$(echo "$email" | sed 's/[^a-zA-Z0-9]/_/g')
    # Generate a unique cookie file name based on the user's email
    #export cookie_file="/cookies_$sanitized_email.txt"
    
    # Login response passthrough
    curl -sS -i -X POST -H "Content-Type: text/xml; charset=UTF-8" -H "Cookie: $HTTP_COOKIE" -d "<login><email>$email</email><password>$password</password></login>" restapi/login | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
    
    sed 's/\[LOGIN_STATUS\]/Logged In/' login-status.html
}


# MARK: - LOGOUT OK
do_logout() {
    # Logout to browser passthrough
    curl -sS -i -X POST -H "Content-Type: text/xml; charset=UTF-8" -H "Cookie: $HTTP_COOKIE" restapi/logout | egrep -v '^HTTP\/.*$' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
    
    sed 's/\[LOGIN_STATUS\]/Logged Out/' login-status.html
}


# MARK: - GET DIKTS OK
get_dikt() {
# Parse diktID from HTML form
local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')

# Is DiktID defined
if [[ -n $diktID ]]; then
    # Validate that the variable is numeric
    if [[ $diktID =~ ^[0-9]+$ ]]; then
        curl -sS -i "restapi/dikt/$diktID" | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
    fi
# If no ID specified, request all dikt
else
    curl -sS -i restapi/dikt | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
fi
}


# MARK: - ADD NEW DIKT OK
add_dikt() {
    # Parse new title
    local title_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')
    # Decode title
    local title=$(echo "$title_encoded" | sed 's/%/\\x/g' | xargs -0 printf "%b")
    # Add dikt and Write return to browser
    curl -sS -i -X POST -H "Content-Type: text/xml; charset=UTF-8" -H "Cookie: $HTTP_COOKIE" -d "<title>$title</title>" restapi/dikt | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
}


# MARK: - EDIT DIKT OK
edit_dikt_from_id() {
    # Parse new title
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    local title_encoded=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "title") {print $(i+1); break}}')
    # Decode title
    local title=$(echo "$title_encoded" | sed 's/%/\\x/g' | xargs -0 printf "%b")

    # Edit dikt and Write return to browser
    curl -sS -i -X PUT -H "Content-Type: text/xml; charset=UTF-8" -H "Cookie: $HTTP_COOKIE" -d "<dikt><title>$title</title></dikt>" "restapi/dikt/$diktID" | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
}


# MARK: - DELETE DIKT OK
delete_dikt_from_id() {
    # Parse diktID
    local diktID=$(echo "$HTTP_BODY" | awk -F'[=&]' '{for(i=1; i<=NF; i++) if ($i == "diktID") {print $(i+1); break}}')
    # Delete dikt and Write reply to browser
    curl -sS -i -X DELETE -H "Cookie: $HTTP_COOKIE" "restapi/dikt/$diktID" | egrep -v '(^HTTP\/.*$)' | sed 's/Transfer\-Encoding.*/Connection\: close/ig'
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
                
            /status)
                echo "Content-Type: text/html"
                echo
                build_html
                cat login-status.html
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
