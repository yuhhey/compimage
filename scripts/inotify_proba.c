#include <sys/inotify.h>
#include <errno.h>
#include <stdlib.h>
#include <limits.h>
#include <sys/stat.h>
#include <stdio.h>
#include <string.h>

void main(int argc, char *argv[])
{
  int notify_event_queue_fd = inotify_init();
  int media_watch_fd;
  int hiba = 0;
  struct inotify_event *media_event;


  if (2 != argc){
    printf("Usage: %s dir_name\n", argv[0]);
    exit(1);
  }
  if (-1 == notify_event_queue_fd){
    hiba=errno;
    printf("inotify_init failed: %s\n", strerror(hiba));
    exit(1);
  }

  media_watch_fd =  inotify_add_watch(notify_event_queue_fd,
				      argv[1],
				      IN_CREATE);
  if (-1 == media_watch_fd){
    hiba = errno;
    printf("inotify_add_watch failed: %s\n",
	   strerror(hiba));
    exit(1);
  }
  int i = 0;
  /* NAME_MAX: fájlnév maximális hossza karakterben. +1 a záró 0-hoz */
  media_event = malloc(sizeof(struct inotify_event) + NAME_MAX + 1);
  while(1){
    /* a read buffernek elég hosszúnak kell lennie, hogy tárolni tudjon egy teljes patht
       ellenkező esetben ha nincs elég hely a read INVAL-lal fog visszatérni */
    int result = read(notify_event_queue_fd,
		      media_event,
		      sizeof(struct inotify_event) + NAME_MAX + 1);
    if (-1 == result){
      printf("read failed: %s\n", strerror(errno));
      exit(1);
    }
    if (IN_ISDIR & media_event->mask){
      //      printf("%d bytes read\n", result);
      //      printf("FD: %d\n", media_event->wd);
      //      printf("Event mask: %x\n", media_event->mask);
      //      printf("Cookie: %d\n", media_event->cookie);
      //      printf("Length:%d\n", media_event->len);
      printf("%s\n", media_event->name);
      exit(0);
      //      i++;
      //      printf("Sorszám: %d\n\n", i);
    }
    //    printf("%s\n", media_event->name);
/* szimbolikus linkeket is fel kell ismerni */
    struct stat stat_buf;
    char teljes_path[NAME_MAX+1];

    sprintf(teljes_path,
	    "%s/%s",
	    argv[1],
	    media_event->name);
    if (lstat(teljes_path, &stat_buf)){
      perror("lstat");
      exit(-1);
    }
    switch(stat_buf.st_mode & S_IFMT) {
    case S_IFLNK:
      printf("%s\n", media_event->name);
      exit(0);
      break;
    }
  }
}
