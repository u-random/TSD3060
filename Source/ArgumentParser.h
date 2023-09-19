//
//  ArgumentParser.h
//  TSD3060-Webserver-1
//
//  Created by Isak Haukeland on 11/09/2023.
//

#ifndef ArgumentParser_h
#define ArgumentParser_h

#include <stdio.h>

// MARK: - Declarations

typedef enum {
    action_start,
    action_stop
} Action_T;

void ArgumentParser_help(void);
Action_T ArgumentParser_handleArguments(int argc, char **argv);



#endif /* ArgumentParser_h */
