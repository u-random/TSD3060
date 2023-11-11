#!/bin/bash


# MARK: - OK!
# Function to parse XML using xmllint and xpath
parse_xml() {
    # $1 is expected to be the XML input
    # $2 is expected to be the XPath expression
    
    # XPath views the XML document as a tree of nodes
    echo "$1" | xmllint --xpath "$2" -
}


# Special XML characters should be replaced
escape_xml() {
    local string="$1"
    string="${string//&/&amp;}"
    string="${string//</&lt;}"
    string="${string//>/&gt;}"
    string="${string//\"/&quot;}"
    string="${string//\'/&apos;}"
    echo "$string"
}


# MARK: - OK!
# Function to check credentials and create a session
login() {
    local email="$1"
    local hashed_password= -n "$2" | sha256sum
    
    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Bruker WHERE epostadresse='$email' AND passordhash='$hashed_password';")

    if [[ $valid_credentials -eq 1 ]]; then
        # Generate a session ID token with UUIDGEN
        local session_id=$(uuidgen)
        
        # Set a cookie header with the session_id
        echo "Set-Cookie: session_id=$session_id; Path=/; HttpOnly; Secure"

        # Store session ID in the database for the user
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID='$session_id' WHERE epostadresse='$email';"
        echo "<session>Logged in with sessionID: '$session_id'. Cookie set.</session>"
    else
        echo "<error>Invalid credentials</error>"
    fi
}


# MARK: - OK!
# Function to logout a user
logout() {
    # Get session id from cookie
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    # Get user belonging to session
    local user=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID=$session_cookie;")
    if [[ -n $session_cookie ]]; then
        # Invalidate the session in the database
        sqlite3 $DATABASE_PATH "UPDATE Sesjon SET sesjonsID=NULL WHERE sesjonsID='$session_id';"
        # Send a header to remove the cookie
        echo "Set-Cookie: session_id=; Path=/; HttpOnly; Secure; Expires=Thu, 01 Jan 1970 00:00:00 GMT"
        # Respond to confirm the user has been logged out
        echo "<response>User '$user' logged out</response>"
    fi
}


# MARK: - OK!
# Function to get a dikt from ID and return proper XML
get_dikt_from_id() {
    local diktID="$1"
    # Fetch the dikt with DiktID
    if [[ -n $diktID ]]; then
        # Validate that the variable is numeric
        if [[ $diktID =~ ^[0-9]+$ ]]; then
            local dikt=$(sqlite3 $DATABASE_PATH "SELECT dikt FROM Dikt WHERE diktID=$diktID;")
            # Prints Dikt if exists, error if not
            if [ -n "$dikt" ]; then
                dikt=$(escape_xml "$dikt")
                echo "<dikt id=\"$diktID\">$dikt</dikt>"
            else
                echo "<error>Dikt not found</error>"
            fi
        # Prints errormessage if diktID is not a number
        else
            echo "<error>Invalid Dikt ID. It has to be a number.</error>"
        fi
    # If no ID specified, send all dikt
    else
        local dikts=$(sqlite3 $DATABASE_PATH "SELECT diktID, dikt FROM Dikt;")
        echo "<diktene>"
        # SQLITE is pipe-seperated
        while IFS='|' read -r diktID dikt; do
            dikt=$(escape_xml "$dikt")
            echo "<dikt id=\"$diktID\">$dikt</dikt>"
        done <<< "$dikts"
        echo "</diktene>"
}


# MARK: - OK!
# Function to add a new dikt
add_dikt() {
    local new_dikt="$1"
    # Get user belonging to session
    local email=$(get_user | awk '{print $2}')
    
    # If the user is logged in
    if is_logged_in; then
        # Insert the new dikt into the database
        sqlite3 $DATABASE_PATH "INSERT INTO Dikt (dikt, epostadresse) VALUES ('$new_dikt', '$email');"
        
        echo "<message>SQLite database updated.</message>"
    else
        echo "<error>You're not logged in. Log in to add a new dikt.</error>"
    fi
}


# Function edit existing dikt
edit_dikt_from_id() {
    local diktID="$1"
    local new_title="$1"

    # Get session id from cookie
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")
    local user_match=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Dikt WHERE epostadresse='$email' AND diktID='$diktID';")

    # If the user is logged in
    if is_logged_in; then
        if [[ $user_match -eq 1 ]]; then
            # Update dikt with new information
            sqlite3 $DATABASE_PATH "UPDATE Dikt (dikt, epostadresse) VALUES ('$new_dikt', '$email');"
            
            echo "<message>SQLite database updated.</message>"
        else
            echo "<error>You can't change someone elses dikt.</error>"
        fi
    else
        echo "<error>You're not logged in. Log in to edit dikts.</error>"
    fi
    
    
    
}


# TODO: Update with logged in logic to reduce repetition in functions above
# Test if user is logged in and session is valid
is_logged_in() {
    # Get session id from cookie
    local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')
    
    # Check if session_cookie is set
    if [ -z "$session_cookie" ]; then
        return 1 # Not logged in if the session cookie is empty
    fi

    # Get user belonging to session
    local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

    # Check credentials against the database
    local valid_credentials=$(sqlite3 $DATABASE_PATH "SELECT COUNT(*) FROM Sesjon WHERE epostadresse='$email' AND sesjonsID='$session_cookie';")

    # If the user is logged in
    if [[ $valid_credentials -eq 1 ]]; then
        return 0 # Logged in
    else
        return 1 # Not logged in
    fi
}


# Get the current User based on session id in HTTP header
get_user() {
    # Get session id from cookie
        local session_cookie=$(printf "%s\n" "$HTTP_COOKIE" | grep -o 'session_id=[^;]*' | sed 's/session_id=//')

        # Check if session_cookie is set
        if [ -z "$session_cookie" ]; then
            echo "<error>No session</error>"
            return 1
        fi

        # Get user belonging to session
        local email=$(sqlite3 $DATABASE_PATH "SELECT epostadresse FROM Sesjon WHERE sesjonsID='$session_cookie';")

        # Check if email is retrieved
        if [ -z "$email" ]; then
            echo "<error>No user found</error>"
            return 1
        fi

        echo "$session_cookie $email"
    
}


DATA_DIR="./" # Data directory path
DATABASE_PATH="$DATA_DIR/DiktDatabase.db"

# RESTful routing logic
METHOD=$(echo "$REQUEST_METHOD")
URI=$(echo "$REQUEST_URI" | awk -F'?' '{print $1}')
QUERY_STRING=$(echo "$REQUEST_URI" | awk -F'?' '{print $2}')


# REST API logic
case $METHOD in
    # Handle GET request
    GET)
        # Matches both /dikt and /dikt/{id} where {id} is a number
        if [[ "$URI" =~ ^/dikt(/([0-9]+))?$ ]]; then
            # Extract diktID if provided, else this will be an empty string
            diktID=${BASH_REMATCH[2]}
            get_dikt_from_id "$diktID"
        else
            echo "<error>Invalid request. Use /dikt for all dikts or /dikt/{id} for a specific dikt.</error>"
        fi
    ;;
    
    
    # Handle POST request
    POST)
        read -r data
        # Login functionality
        case "$URI" in
            # Logoin logic
            /login)
                # Extract email and password from XML body
                EMAIL=$(parse_xml "$HTTP_BODY" "//email/text()")
                PASSWORD=$(parse_xml "$HTTP_BODY" "//password/text()")
                # Run Login funcition
                login "$EMAIL" "$PASSWORD"
                ;;


            # Logout logic
            /logout)
                # Run logout function
                logout
                ;;
    

            # Adding a new dikt functionality
            /dikt)
                TITLE=$(parse_xml "$HTTP_BODY" "//dikt/text()")

                add_dikt "$TITLE"

        esac
    

        # Handle PUT request
        PUT)
            read -r data

            # Should match only when {id} is a number
            if [[ "$URI" =~ ^/dikt(/([0-9]+))$ ]]; then
                # Extract diktID if provided
                diktID=${BASH_REMATCH[2]}
                TITLE=$(parse_xml "$HTTP_BODY" "//dikt/text()")


                edit_dikt_from_id "$diktID" "$TITLE"
            else
                echo "<error>Unable to update. {id} for dikt/{id} has to be a number.</error>"
            fi
            


            session_id=$(echo "$data" | grep -oP '<sesjon>\K[^<]+')
            user_email=$(is_logged_in "$session_id")
            diktID=$(echo "$URI" | grep -oP 'dikt/\K[0-9]+')

            if [ -n "$user_email" ] && [[ $diktID =~ ^[0-9]+$ ]]; then
                dikt_content=$(echo "$data" | grep -oP '<dikt>\K[^<]+')
                # Update poem in the database
                sqlite3 $DATABASE_PATH "UPDATE Dikt SET dikt='$dikt_content' WHERE diktID=$diktID AND epostadresse='$user_email';"
                echo "<success>Dikt updated</success>"
            else
                echo "<error>User not logged in or invalid diktID</error>"
            fi
            ;;

    
    
    
        

        # For login:
        if [[ $URI == '/login' ]]; then
            # Extract email and password from XML body
            EMAIL=$(parse_xml "$HTTP_BODY" "//email/text()")
            PASSWORD=$(parse_xml "$HTTP_BODY" "//password/text()")
            login "$EMAIL" "$PASSWORD"
        fi

        # Extract the session_id from the Cookie header
        session_id=$(echo "$HTTP_COOKIE" | grep -o 'sesjonsID=[^;]*' | cut -d'=' -f2)

        # Query the database to validate the session
        valid_session=$(sqlite3 mydb.sqlite "SELECT COUNT(*) FROM Sesjon WHERE sesjonsID='$session_id';")


        # For adding a poem:
        if [[ $URI == '/poems' ]]; then
            POEM=$(parse_xml "$HTTP_BODY" "//poem/text()")
            SESSION_ID=$(parse_xml "$HTTP_BODY" "//session_id/text()")
            add_poem "$POEM" "$SESSION_ID"
        fi
        ;;

    # Include other methods and routes as needed
esac

# Make sure to set Content-Type to application/xml for all responses
# And to use the correct XML structure in responses

# Use this command to test login:
# curl -X POST -H "Content-Type: text/xml" -d '<login><email>demo@demomail.com</email><password>admin</password></login>' http://localhost/login
