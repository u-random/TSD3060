PROG=TSD3060
CC = clang
CFLAGS = -g -Wall
LDFLAGS = -I./Source
SRCS = 	Source/main.c \
		Source/Config.c \
		Source/ArgumentParser.c \
		Source/HttpStatus.c \
		Source/Mime.c \
		Source/Server.c \
		Source/Http.c \
		Source/File.c
OBJS = $(SRCS:.c=.o)

# Targets

$(PROG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

.c.o:
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: clean
clean:
	rm -f *.o $(PROG)
