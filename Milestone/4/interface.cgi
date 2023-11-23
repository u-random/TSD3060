
#!/bin/bash

# HEADERS
echo "Content-Type: text/xml"


write_body() {
    # Blank line to separate from header
    echo ""
    # First argument to function is message
    echo "$1"
}

write_html_error() {
    # Blank line to separate from header
    echo ""
    
    # Write contents of argument inside proper HTML
    cat << EOF
    <!doctype html>
    <html>
        <head>
            <meta charset='utf-8'>
            <title>Error message</title>
        </head>
        <body>
            <h1>$1</h1>
        </body>
    </html>
    EOF

}

# Takes a title as an argument
html_begin() {
    # Blank line to separate from header
    echo ""
    
    # Write HTML header
    cat << EOF
    <!doctype html>
    <html>
        <head>
            <meta charset='utf-8'>
            <title>$1</title>
        </head>
        <body>
    EOF
    
}

html_end() {
    cat << EOF
        </body>
    </html>
    EOF
}

# MARK: - Start Page V
# This function is made to show all or single dikts, and a login box.
start_page() {
    get_dikt
    login_form
}













# MARK: - LOGIN V
# Function to check credentials and create a session
do_login() {
    # Extract email and password from XML body
    local email=$(parse_xml "$HTTP_BODY" "//email/text()")
    local password=$(parse_xml "$HTTP_BODY" "//password/text()")
    local password_hash=$(echo -n $password | sha256sum | cut -d ' ' -f 1)

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Bruker WHERE epostadresse='$email' AND passordhash='$password_hash';")
    
    if [[ $valid_credentials -eq 1 ]]; then
        # Check if user is logged in
        if is_logged_in; then
            # Never sent
            write_body "<message>Hello, '$email'! You're already logged in!</message>"
        else
            # Generate a session ID token with UUIDGEN
            local session_cookie=$(uuidgen)
            
            # Set a cookie HEADER with the session_id
            echo "Set-Cookie: session_id=$session_cookie; Path=/; HttpOnly; Secure"

            # Store session ID in the database for the user
            sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID='$session_cookie' WHERE epostadresse='$email';"
            
            # Write welcome message
            write_body "<message>Welcome back, '$email'! You're logged in!</message>"
            echo "<debug>Cookie set with uuid: '$session_cookie'</debug>"
        fi
    else
        write_body "<error>Invalid credentials</error>"
        echo "<debug>Passhash: '$password_hash'</debug>"
        echo "<debug>Pass: '$password'</debug>"
        echo "<debug>Email: '$email'</debug>"
    fi
}


# MARK: - LOG USER OUT V
# Function to logout a user
do_logout() {
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get session id from cookie
    local session_cookie=$(echo "$user_data" | awk '{print $1}')
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
    
    # If user is logged in
    if is_logged_in; then
        # Invalidate the session in the database
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID=NULL WHERE sesjonsID='$session_cookie';"
        # Send a header to remove the cookie
        echo "Set-Cookie: session_id=; Path=/; HttpOnly; Secure; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        # Respond to confirm the user has been logged out
        write_body "<message>User '$email' logged out.</message>"
    else
        # Respond to confirm the user has been logged out
        write_body "<message>No session detected.</message>"
    fi
}




# TODO: - How to check for logged in status?

# MARK: - GET DIKT, ONE OR ALL OK
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
            write_html_error "Invalid Dikt ID. It has to be a number."
        fi
    # If no ID specified, send all dikt
    else
        local xml_response=$(curl -i localhost:8280/dikt)
        dikt_from_xml "$xml_response"
    fi
}

# MARK: - To print dikts, used in get_dikt OK
dikt_from_xml() {

html_begin "Dikts"

# Use the response in an awk script
echo "$1" | awk '
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

html_end

}






# MARK: - ADD A NEW DIKT V
add_dikt() {
    # Get session id from cookie environment variable
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    local new_title=$(parse_xml "$HTTP_BODY" "//title/text()")
    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")
    
    # If the user is logged in
    if is_logged_in; then
        # Insert the new dikt into the database
        sqlite3 $DATABASE_PATH "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$new_title', '$email');"
        
        write_body "<message>SQLite database updated.</message>"
    else
        write_body "<error>You're not logged in. Log in to add a new dikt.</error>"
    fi
}


# MARK: - EDIT AN EXISTING DIKT V
edit_dikt_from_id() {
    # Extract diktID from array variable Bash_rematch with result of regex match
    local diktID=${BASH_REMATCH[2]}
    local new_title=$(parse_xml "$HTTP_BODY" "//title/text()")
    
    # Check if diktID exists
    local id_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE diktID='$diktID';")
    
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
        
    # Check if user is owner of dikt with ID = diktID
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $id_match -eq 1 ]]; then
            if [[ $user_match -eq 1 ]]; then
                # Update dikt with new information
                sqlite3 $DATABASE_PATH "UPDATE Dikt SET dikt = '$new_title' WHERE diktID = $diktID;"

                write_body "<message>SQLite database updated.</message>"
                #echo "<debug>Data: '$new_title', user $email</debug>"
            else
                write_body "<error>You can't change someone elses dikt.</error>"
            fi
        else
            write_body "<error>This dikt does not exist. Use an existing id for changes.</error>"
        fi
    else
        write_body "<error>You're not logged in. Log in to edit dikts.</error>"
    fi
}


# MARK: - DELETE A DIKT V
# This function is made to delete single dikts based on id
delete_dikt_from_id() {
    # Extract diktID if provided
    local diktID=${BASH_REMATCH[2]}
    
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
    
    # Check if user is owner of dikt with ID = diktID. 1 if vaild
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -eq 1 ]]; then
            # Delete given dikt
            sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE diktID=$diktID AND epostadresse='$email';"
            
            write_body "<message>SQLite entry deleted.</message>"
        else
            write_body "<error>You can't delete someone elses dikt.</error>"
        fi
    else
        write_body "<error>You're not logged in. Log in to delete entries.</error>"
    fi
}

# RESTful routing logic
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')


# MARK: - CASE statement V
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
