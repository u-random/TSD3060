
PROG=TSD3060
CC = clang
OS = $(shell uname|tr a-z A-Z)
DIST = Distribution

# Compiling setup
CFLAGS = -g -Wall -D$(OS)

# Default to dynamic linking
LDFLAGS := -I./Source

SRCS =  Source/main.c \
        Source/Config.c \
        Source/ArgumentParser.c \
        Source/HttpStatus.c \
        Source/Mime.c \
        Source/Server.c \
        Source/Http.c \
        Source/File.c
OBJS = $(SRCS:.c=.o)

# Conditional logic for Linux
ifeq ($(OS),LINUX)
    LDFLAGS += -static
endif

# Targets
all: $(PROG)

# kommandoer for å starte container
m2: $(PROG)
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


