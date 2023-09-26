//
//  Http.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 07/09/2023.
//

#include "Config.h"

#include "File.h"
#include "Http.h"

// MARK: - Private methods

// Returns method type
static Http_Method _parseMethod(char *method) {
    if (strcasecmp(method, "GET") == 0) {
        return HTTP_GET;
    } else if (strcasecmp(method, "POST") == 0) {
        return HTTP_POST;
    } else if (strcasecmp(method, "PUT") == 0) {
        return HTTP_PUT;
    } else if (strcasecmp(method, "DELETE") == 0) {
        return HTTP_DELETE;
    } else if (strcasecmp(method, "HEAD") == 0) {
        return HTTP_HEAD;
    } else {
        return HTTP_UNKNOWN;
    }
}



// MARK: - Public methods

// Return a RFC1123 date string
char *Http_date(char *result, int size) {
    time_t now;
    struct tm converted;
    time(&now);
    if (strftime(result, size, RFC1123, gmtime_r(&now, &converted)) <= 0)
        *result = 0;
    return result;
}



// Creates new header and adds it to the end of the headers list in Request_T (Fra Phind)
void Http_addHeader(Header_T headers, char *name, char *value) {
    Header_T new_header = malloc(sizeof(*new_header));      // Create a new header node with malloc
    new_header->name = strdup(name);                        // Copies "name" from input with strdup
    new_header->value = strdup(value);                      // Copies "value" from input
    new_header->next = NULL;                                // Setting header to last item in linked list
    
    // Find the last header in the list by iterating through the existing headers in the request struct
    Header_T last_header = headers;
    while (last_header && last_header->next) last_header = last_header->next;
    
    // Add the new header to the end of the list. Checks if list is empty
    if (last_header)
        last_header->next = new_header; // Sets next field to point to the new header insteadof null
    else
        headers = new_header;  // This is the first header in the list. This is processed if list is empty.
}



// Read full request and fill out Request_T object
Request_T Http_getRequest(Request_T request, Response_T response) {
    // 8k buffer
    char buffer[8192];
    // Read request line from the socket.
    // TODO: Implement timeout and DDoS protection
    if (!fgets(buffer, sizeof(buffer), request->input_stream)) {
        Http_sendError(request, SC_INTERNAL_SERVER_ERROR, "Cannot read from socket\n");
    }
    char method[16] = {};
    char path[PATH_MAX] = {};
    char version[16] = {};
    
    int result = sscanf(buffer, "%s %s %s", method, path, version);
    if (result != 3) {
        Http_sendError(request, SC_BAD_REQUEST, NULL);
    }
    // Fill out the request struct
    request->http_method = _parseMethod(method);  // Running the parseMethod to check against any existing
    request->path = strdup(path);
    request->http_version = strdup(version);
    
    // Parse the headers
    while (fgets(buffer, sizeof(buffer), request->input_stream)) {
        if (strcmp(buffer, "\r\n") == 0 || strcmp(buffer, "\n") == 0)
            break;
        char name[128] = {};
        char value[4096] = {};
        // Buffer is on format: name:value\r\n
        result = sscanf(buffer, "%[^:]:%s", name, value);
        if (result != 2) {
            Http_sendError(request, SC_BAD_REQUEST, "Invalid header format\n");
        }
        // Add the header to the request struct
        Http_addHeader(request->headers, name, value);
    }
    return request;
}



// Handle Request: find file, check if it exists and set real path
Request_T Http_handleRequest(Request_T request) {
    // TODO: Make compatible with meme.types extentions
    // Check that file extension is .asis
    if (!File_is_asis(request->path)) {
        Http_sendError(request, SC_NOT_FOUND, "Requested file is not an \"asis\" file\n");
    }
    char buffer[PATH_MAX] = {};
    snprintf(buffer, sizeof(buffer), "%s/%s", Server.web_root, request->path);
    // Does file exist?
    if (!File_exist(buffer)) {
        Http_sendError(request, SC_NOT_FOUND, "Requested file not found\n");
    }
    request->file_path = strdup(buffer);
    return request;
}



// Write response (write headers, write file)
size_t Http_writeResponse(Request_T request) {
    char buffer[1500]; // One TCP frame
    Response_T response = request->response;
    FILE *file = fopen(request->file_path, "r");
    if (!file) {
        Http_sendError(request, SC_INTERNAL_SERVER_ERROR, "Could not open requested file for reading\n");
    }
    // Write the response headers
    fprintf(response->output_stream, "HTTP/1.1 %d %s\r\n", response->http_status, HttpStatus_description(response->http_status));
    fprintf(response->output_stream, "Content-Type: text/plain\r\n");
    fprintf(response->output_stream, "Content-Length: %lld\r\n", (long long)File_size(request->file_path));
    fprintf(response->output_stream, "Connection: close\r\n");
    fprintf(response->output_stream, "\r\n");
    // Read and send file to our output_stream
    size_t bytes_read = 0;
    off_t bytes_written = 0;
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        size_t n = fwrite(buffer, 1, bytes_read, response->output_stream);
        if (n == 0) {
            Http_sendError(request, SC_INTERNAL_SERVER_ERROR, "Could not write file\n");
        }
        bytes_written += n;
    }
    fflush(response->output_stream);
    return bytes_written;
}



// Send a canned system error message and exit
void Http_sendError(Request_T request, Http_Status status_code, const char *error) {
    char date[32];
    Http_date(date, 31);
    Response_T response = request->response;
    fprintf(response->output_stream,
            "%s %d %s\r\n"
            "Date: %s\r\n"
            "Connection: close\r\n"
            "Content-Type: text/html\r\n\r\n"
            "<html>\r\n<head><title>%d %s</title></head>\r\n"
            "<body bgcolor=\"white\">\r\n<h2>%s</h2>%s</body>\r\n"
            "</html>\r\n",
            request->http_version,
            status_code,
            HttpStatus_description(status_code),
            date,
            status_code,
            HttpStatus_description(status_code),
            HttpStatus_description(status_code),
            error ? error : "");
    
    // Writing message to standard error and logfile
    fprintf(stderr, "Error: %d %s - %s\n", status_code, HttpStatus_description(status_code), error ? error : "");
    fflush(response->output_stream);
    if (Server.log) {
        fprintf(Server.log, "Error: %d %s - %s\n", status_code, HttpStatus_description(status_code), error ? error : "");
        fflush(Server.log);
    }
    shutdown(request->socket_descriptor, SHUT_RDWR);
    close(request->socket_descriptor);
    _exit(0);
}
