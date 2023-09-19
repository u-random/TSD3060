//
//  HttpStatus.c
//  TSD3060-Webserver-1
//
//  Created by Isak Lars Haukeland on 08/09/2023.
//

#include "Config.h"

#include "HttpStatus.h"


// MARK: - HTTP status code description
// Returns a short description of the HTTP status code
const char *HttpStatus_description(Http_Status code) {
    switch (code) {
        case  SC_CONTINUE:
            return "Continue";
        case  SC_SWITCHING_PROTOCOLS:
            return "Switching Protocols";
        case  SC_OK:
            return "OK";
        case  SC_CREATED:
            return "Created";
        case  SC_ACCEPTED:
            return "Accepted";
        case  SC_NON_AUTHORITATIVE:
            return "Non-Authoritative Information";
        case  SC_NO_CONTENT:
            return "No Content";
        case  SC_RESET_CONTENT:
            return "Reset Content";
        case  SC_PARTIAL_CONTENT:
            return "Partial Content";
        case  SC_MULTIPLE_CHOICES:
            return "Multiple Choices";
        case  SC_MOVED_PERMANENTLY:
            return "Moved Permanently";
        case  SC_MOVED_TEMPORARILY:
            return "Moved Temporarily";
        case  SC_SEE_OTHER:
            return "See Other";
        case  SC_NOT_MODIFIED:
            return "Not Modified";
        case  SC_USE_PROXY:
            return "Use Proxy";
        case  SC_TEMPORARY_REDIRECT:
            return "Temporary Redirect";
        case  SC_BAD_REQUEST:
            return "Bad Request";
        case  SC_UNAUTHORIZED:
            return "Unauthorized";
        case  SC_PAYMENT_REQUIRED:
            return "Payment Required";
        case  SC_FORBIDDEN:
            return "Forbidden";
        case  SC_NOT_FOUND:
            return "Not Found";
        case  SC_METHOD_NOT_ALLOWED:
            return "Method Not Allowed";
        case  SC_NOT_ACCEPTABLE:
            return "Not Acceptable";
        case  SC_PROXY_AUTHENTICATION_REQUIRED:
            return "Proxy Authentication Required";
        case  SC_REQUEST_TIMEOUT:
            return "Request Timeout";
        case  SC_CONFLICT:
            return "Conflict";
        case  SC_GONE:
            return "Gone";
        case  SC_LENGTH_REQUIRED:
            return "Length Required";
        case  SC_PRECONDITION_FAILED:
            return "Precondition Failed";
        case  SC_REQUEST_ENTITY_TOO_LARGE:
            return "Request Entity too large";
        case  SC_REQUEST_URI_TOO_LARGE:
            return "Request URI too large";
        case  SC_UNSUPPORTED_MEDIA_TYPE:
            return "Unsupported media type";
        case  SC_RANGE_NOT_SATISFIABLE:
            return "Range not satisfiable";
        case  SC_EXPECTATION_FAILED:
            return "Expectation failed";
        case  SC_INTERNAL_SERVER_ERROR:
            return "Internal Server error";
        case  SC_NOT_IMPLEMENTED:
            return "Not implemented";
        case  SC_BAD_GATEWAY:
            return "Bad Gateway";
        case  SC_SERVICE_UNAVAILABLE:
            return "Service unavailable";
        case  SC_GATEWAY_TIMEOUT:
            return "Gateway Timeout";
        case  SC_VERSION_NOT_SUPPORTED:
            return "Version not supported";
        default:
            return "Unknown status";
    }
}
