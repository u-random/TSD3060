#!/bin/bash

# TODO: HTTP only session cookies might cause a problem with javascript

# HTTP HEADERS
echo "Content-Type: text/xml"

# MARK: - Parse XML with XPATH
parse_xml() {
    # $1 is XML input,$2 is the XPath expression
    local result=$(echo "$1" | xmllint --xpath "$2" -)
    if [ $? -ne 0 ]; then
        echo "error"
    else
        echo "$result"
    fi
}


test_xmllint(){
    # Check if xmllint is available
    if ! command -v xmllint &> /dev/null; then
        write_start "<error>Xmllint not found.</error>"
        echo "<message> To download, do: \"apt -y install libxml2-utils\"</message>"
        write_end
        return 1
    fi
}


# Summary: Produce a different DTD location based on environment
detect_environment() {
    # Check if running inside Docker
    if [ -f /.dockerenv ]; then
        # Docker environment
        echo "http://host.docker.internal:8080/response.dtd"
    else
        # Host environment
        echo "http://localhost:8080/response.dtd"
    fi
}


# MARK: - Refactor Special XML Characters
# Summary: Special XML characters replaced on output from Database
escape_xml() {
    local string="$1"
    string="${string//&/&amp;}"
    string="${string//</&lt;}"
    string="${string//>/&gt;}"
    string="${string//\"/&quot;}"
    string="${string//\'/&apos;}"
    echo "$string"
}


# MARK: - Writing Top of Body
write_start() {
    # Blank line to separate from header
    echo ""
    
    # Echo XML schema reference
    echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
    echo "<!DOCTYPE root SYSTEM \"$(detect_environment)\">"
    
    # Echo root element start tag
    echo "<root>"
    
    # First argument to function is message
    if [ -n "$1" ]; then
        echo "$1"
    fi
}


# MARK: - Writing Bottom of Body
write_end() {
    if [ -n "$1" ]; then
        echo "$1"
    fi
    echo "</root>"
}


# MARK: - Log In
# Summary: Check input credentials and create a session
do_login() {
    # Extract email and password from XML body, and hash password
    local email=$(parse_xml "$HTTP_BODY" "//email/text()")
    local password=$(parse_xml "$HTTP_BODY" "//password/text()")
    local password_hash=$(echo -n $password | sha256sum | cut -d ' ' -f 1)

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Bruker WHERE epostadresse='$email' AND passordhash='$password_hash';")
    
    if [[ $valid_credentials -eq 1 ]]; then
        # Check if user is already logged in
        if is_logged_in; then
            write_start "<message>Hello, '$email'! You're already logged in!</message>"
            write_end
        else
            # Generate a session ID token
            local session_cookie=$(uuidgen)
            
            # Set a cookie Header
            echo "Set-Cookie: session_id=$session_cookie; Path=/; HttpOnly;"

            # Store session ID token in the database
            sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID='$session_cookie' WHERE epostadresse='$email';"
            
            # Write welcome message
            write_start "<message>Welcome back, '$email'! You're logged in!</message>"
            write_end "<debug>Cookie set with uuid: '$session_cookie'</debug>"
        fi
    else
        write_start "<error>You provided invalid credentials!</error>"
        echo "<debug>Email provided: '$email'</debug>"
        echo "<debug>Password provided: '$password'</debug>"
        write_end "<debug>Password hash generated: '$password_hash'</debug>"
    fi
}


# MARK: - Check Logged In Status
# Summary: Test if user is logged in and session is valid
is_logged_in() {
    # Get session id from cookie
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    
    # Check if session_cookie is set
    if [ -z "$session_cookie" ]; then
        # Not logged in if the session cookie is empty
        return 1
    fi

    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

    # Check if session is set in database
    local valid_session=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Sesjon WHERE epostadresse='$email' AND sesjonsID='$session_cookie';")

    # If the user is logged in
    if [[ $valid_session -eq 1 ]]; then
        return 0 # Logged in
    else
        return 1 # Not logged in
    fi
}


# MARK: - Log Out
do_logout() {
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    local session_cookie=$(echo "$user_data" | awk '{print $1}')
    local email=$(echo "$user_data" | awk '{print $2}')
    
    # If user is logged in
    if is_logged_in; then
        # Invalidate the session in the database
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID=NULL WHERE sesjonsID='$session_cookie';"
        
        # Send a header to remove the cookie
        echo "Set-Cookie: session_id=; Path=/; HttpOnly; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        
        # Respond with logout confirmation
        write_start "<message>User '$email' logged out.</message>"
        write_end
    else
        write_start "<message>No session detected. Log in to log out.</message>"
        write_end
    fi
}


# Mark: - Get User Data
# Summary: Get the current user based only on session id from HTTP.
get_user() {
    # Get session id from cookie environment variable
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')

    # Check if session_cookie is set
    if [ -z "$session_cookie" ]; then
        return 1
    fi

    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

    # Check if email is retrieved
    if [ -z "$email" ]; then
        return 1
    fi

    # Print out cookie and email in one string
    echo "$session_cookie $email"
}


# MARK: - Get Dikts
# Summary: Get a dikt from ID, if any, and return proper XML
get_dikt() {
    # Extract diktID from array variable Bash_rematch with result of regex match from case
    local diktID=${BASH_REMATCH[2]}
    # Fetch the dikt with DiktID
    if [[ -n $diktID ]]; then
        # Validate that the variable is numeric
        if [[ $diktID =~ ^[0-9]+$ ]]; then
            local single_output=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt, epostadresse FROM Dikt WHERE diktID=$diktID;")
            # Prints Dikt if exists, error if not
            if [ -n "$single_output" ]; then
                write_dikt "$single_output"
            else
                write_start "<error>Dikt not found</error>"
                write_end
            fi
        # Prints errormessage if diktID is not a number
        else
            write_start "<error>Invalid Dikt ID. It has to be a number.</error>"
            write_end
        fi
    # If no ID specified, send all dikt
    else
        local all_output=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt, epostadresse FROM Dikt;")
        write_dikt "$all_output"
    fi
}


# Summary: Small function for writing XML tables
write_dikt() {
    write_start
    # SQLITE is pipe-seperated
    while IFS='|' read -r diktID dikt email; do
        local dikt=$(escape_xml "$dikt")
        echo "<dikt><id>$diktID</id><titlen>$dikt</titlen><email>$email</email></dikt>"
    done <<< "$1"
    write_end
}


# MARK: - ADD A NEW DIKT
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
        
        write_start "<message>SQLite database updated.</message>"
        write_end
    else
        write_start "<error>You're not logged in. Log in to add a new dikt.</error>"
        write_end
    fi
}


# MARK: - EDIT AN EXISTING DIKT
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

                write_start "<message>SQLite database updated.</message>"
                write_end
                #echo "<debug>Data: '$new_title', user $email</debug>"
            else
                write_start "<error>You can't change someone elses dikt.</error>"
                write_end
            fi
        else
            write_start "<error>This dikt does not exist. Use an existing id for changes.</error>"
            write_end
        fi
    else
        write_start "<error>You're not logged in. Log in to edit dikts.</error>"
        write_end
    fi
}


# TODO: - Cleanup
# MARK: - DELETE A DIKT
# Summary: This function is made to delete single dikts based on id
delete_dikt_from_id() {
    # Extract diktID if provided
    local diktID=${BASH_REMATCH[2]}
    
    # Get the session cookie and user email from get_user function
    local user_data=$(get_user)
    # Get user belonging to session
    local email=$(echo "$user_data" | awk '{print $2}')
    
    # Check if user is owner of dikt with ID = diktID. 1 if vaild
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -ge 1 ]]; then
            # Delete the dikt with DiktID
            if [[ -n $diktID ]]; then
                # Validate that the variable is numeric
                if [[ $diktID =~ ^[0-9]+$ ]]; then
                    local dikt_exists=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")
                    # Deletes Dikt if exists, error if not
                    if [ $dikt_exists -eq 1 ]; then
                        sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE diktID=$diktID AND epostadresse='$email';"
                        write_start "<message>A single SQLite entry was deleted.</message>"
                        write_end
                    else
                        write_start "<error>Dikt not found</error>"
                        write_end
                    fi
                # Prints errormessage if diktID is not a number
                else
                    write_start "<error>Invalid Dikt ID. It has to be a number.</error>"
                    write_end
                fi
            # If no ID specified, Delete all dikt
            else
                sqlite3 $DATABASE_PATH "DELETE FROM Dikt WHERE epostadresse='$email';"
                write_start "<message>All your entries deleted.</message>"
                write_end
            fi
        else
            write_start "<error>You can't delete someone elses dikt.</error>"
            write_end
        fi
    else
        write_start "<error>You're not logged in. Log in to delete entries.</error>"
        write_end
    fi
}


# Data directory paths
DATA_DIR="./"
DATABASE_PATH="$DATA_DIR/DiktDatabase.db"

# RESTful routing logic
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')

# Run to see if parser is availible
test_xmllint

# MARK: - CASE statement
# Summary: REST API logic
case $METHOD in
    # MARK: - HTTP GET request. Matches SQL: SELECT
    GET)
        # REGEX for URI to match: /dikt, /dikt/ and /dikt/{id} where {id} is a number.
        # I later use Bash Rematch to get the ID, if any
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?/?$ ]]; then
            # Run my function to get dikts
            get_dikt
        else
            write_start "<error>Invalid request. Use /dikt for all dikts or /dikt/{id} for a specific dikt.</error>"
            write_end
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
            write_start "<error>Unable to update. {id} for dikt/{id} has to be a number.</error>"
            write_end
        fi
        ;;


    # MARK: - HTTP DELETE request. Matches SQL: DELETE
    DELETE)
        read -r HTTP_BODY
        # Should match only when {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?/?$ ]]; then
            # Run my delete function
            delete_dikt_from_id
        else
            write_start "<error>Faulty request. Remember, {id} has to be a number.</error>"
            write_end
        fi
        ;;
esac
