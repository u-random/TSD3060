PROG=TSD3060
CC = clang
CFLAGS = -g -Wall
LDFLAGS = #v
SRCS = 	main.c \
		Config.c \
		ArgumentParser.c \
		HttpStatus.c \
		Mime.c \
		Server.c \
		Http.c \
		File.c
OBJS = $(SRCS:.c=.o)

# Targets

$(PROG): $(OBJS)
	$(CC) $(LDFLAGS) -o $@ $^

.c.o:
	$(CC) $(CFLAGS) -c $<

.PHONY: clean
clean:
	rm -f *.o $(PROG)
