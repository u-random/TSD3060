
PROG=TSD3060
CC = clang
OS = $(shell uname|tr a-z A-Z) # Makes uppercase
DIST = Distribution

# Compiling setup
CFLAGS = -g -Wall -D$(OS)

# Default to dynamic linking
LDFLAGS = -I./Source
# On Linux, we also allow static linking
STATIC_LDFLAGS = -static

SRCS =  Source/main.c \
        Source/Config.c \
        Source/ArgumentParser.c \
        Source/HttpStatus.c \
        Source/Mime.c \
        Source/Server.c \
        Source/Http.c \
        Source/File.c
OBJS = $(SRCS:.c=.o)

# Conditional logic for Linux and macOS
ifeq ($(OS),LINUX)
    LDFLAGS += $(STATIC_LDFLAGS)
endif
# Targets
all: $(PROG)

# kommandoer for å starte container
container: $(PROG)
	-cp $(PROG) $(DIST)/bin
	./Scripts/Container/milestone-2-container.sh

$(PROG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

.c.o:
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f $(OBJS) $(PROG) $(DIST)/bin/*
	rm -rf tmp/


