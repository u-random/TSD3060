//
//  Http.h
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 07/09/2023.
//

#ifndef Http_h
#define Http_h
#include "HttpStatus.h"

// MARK: - Declarations

typedef enum {
    HTTP_GET,
    HTTP_POST,
    HTTP_PUT,
    HTTP_DELETE,
    HTTP_HEAD,
    HTTP_UNKNOWN
} Http_Method;

typedef struct Header_T {
    char *name;                 // Example, "Host"
    char *value;                // Example, "www.example.com"
    struct Header_T *next;      // Points to next element in list
} *Header_T;

typedef struct Response_T {
    Http_Status http_status;    // Response Status, example "SC_OK" or "200"
    Header_T headers;           // Request headers
    FILE *output_stream;        // Socket output stream. See https://www.gnu.org/software/libc/manual/html_node/Descriptors-and-Streams.html#Descriptors-and-Streams
} *Response_T;

typedef struct Request_T {
    Response_T response;        // Response object, see struct above
    int socket_descriptor;      // Connected socket
    Http_Method http_method;    // HTTP Method, example "GET"
    char *http_version;         // HTTP Version, example "HTTP/1.1"
    char *path;                 // Request path, example "/index.asis"
    Header_T headers;           // Request headers, see struct above
    const char *file_path;      // The path to the file to write
    FILE *input_stream;         // Socket input stream
} *Request_T;

// MARK: - Functions

char *Http_date(char *result, int size);
void Http_addHeader(Header_T headers, char *name, char *value);
Request_T Http_getRequest(Request_T request, Response_T response);
Request_T Http_handleRequest(Request_T request);
size_t Http_writeResponse(Request_T request);
void Http_sendError(Request_T request, Http_Status status_code, const char *error);
const char *HttpStatus_description(Http_Status code);


#endif /* Http_h */
