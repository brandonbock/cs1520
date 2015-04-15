Skip to content
Sign up Sign in This repository
Explore
Features
Enterprise
Blog
 Watch 1  Star 0  Fork 0 Jnapp18/College-Projects
 branch: master  College-Projects/Intro to Operating Systems/File System/filesystem.c
@Jnapp18Jnapp18 on Dec 30, 2014 Adding Projects
1 contributor
RawBlameHistory     678 lines (632 sloc)  16.942 kb
/*
	FUSE: Filesystem in Userspace
	Copyright (C) 2001-2007  Miklos Szeredi <miklos@szeredi.hu>
	This program can be distributed under the terms of the GNU GPL.
	See the file COPYING.
*/

#define	FUSE_USE_VERSION 26

#include <fuse.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <fcntl.h>

//size of a disk block
#define	BLOCK_SIZE 512

//we'll use 8.3 filenames
#define	MAX_FILENAME 8
#define	MAX_EXTENSION 3

//How many files can there be in one directory?
#define	MAX_FILES_IN_DIR (BLOCK_SIZE - (MAX_FILENAME + 1) - sizeof(int)) / \
	((MAX_FILENAME + 1) + (MAX_EXTENSION + 1) + sizeof(size_t) + sizeof(long))
#define BITMAP_SIZE (BLOCK_SIZE*20) // (5 * 2^20)/512 = 10240..
//How much data can one block hold?
#define	MAX_DATA_IN_BLOCK BLOCK_SIZE

//How many pointers in an inode?
#define NUM_POINTERS_IN_INODE ((BLOCK_SIZE - sizeof(unsigned int) - sizeof(unsigned long)) / sizeof(unsigned long))

struct cs1550_directory_entry
{
	char dname[MAX_FILENAME	+ 1];	//the directory name (plus space for a nul)
	int nFiles;			//How many files are in this directory. 
					//Needs to be less than MAX_FILES_IN_DIR

	struct cs1550_file_directory
	{
		char fname[MAX_FILENAME + 1];	//filename (plus space for nul)
		char fext[MAX_EXTENSION + 1];	//extension (plus space for nul)
		size_t fsize;			//file size
		long nStartBlock;		//where the first block is on disk
	} files[MAX_FILES_IN_DIR];		//There is an array of these
};

typedef struct cs1550_directory_entry cs1550_directory_entry;

struct cs1550_disk_block
{
	char bitmap[10240];
	//And all of the space in the block can be used for actual data
	//storage.
	char data[MAX_DATA_IN_BLOCK];
};

typedef struct cs1550_disk_block cs1550_disk_block;
static int getIndexOfDir(cs1550_directory_entry *dir, int i)//returns index or -1 if not found
{
	int res = -1;
	FILE *f = fopen(".directories", "rb");
	if (f == NULL)
		return -1;
	if(fseek(f, sizeof(cs1550_directory_entry) * i, SEEK_SET) == -1)
		return -1;
	if(fread(dir, sizeof(cs1550_directory_entry), 1, f) == 1)
	{
		res = i;
	}
	fclose(f);
	return res;
}
static int fileExists(char *filename, char *extension, cs1550_directory_entry *dir)
{
	int i;
	for(i = 0; i < (*dir).nFiles; i++)
	{
		if(strcmp(filename, (*dir).files[i].fname ) == 0 && strcmp(extension, (*dir).files[i].fext) == 0 )
			return i;
	}
	return -1;
}
static int addFileToDotDir(cs1550_directory_entry *dir, int i)
{
	FILE *f = fopen(".directories", "rb+");
	fseek(f, sizeof(cs1550_directory_entry) * i, SEEK_SET);
	fwrite(dir, sizeof(cs1550_directory_entry),1,f);
	fclose(f);
	return 0; 
}
static int write(const char *buf, size_t size, off_t offset, int index, cs1550_directory_entry *dir)
{		
	offset = offset;
	FILE* f = fopen(".disk", "rb+");
	if((*dir).files[index].nStartBlock < 10239)
	{
		(*dir).files[index].fsize = size;			
		int i;
		int s = (int)size;
		char readChar;
		char c = '1';
		while(s > 0)
		{
			for (i = 0; i < 10240; i++)
			{
				fseek(f, i, SEEK_SET);
				fread(&readChar, sizeof(char), 1, f);
				if(readChar == '\0')
					break;
			}
		  	fseek(f, i, SEEK_SET);
			fputs( &c, f);
			s = s - 512;
		}
		if( (*dir).files[index].nStartBlock == '\0')
			(*dir).files[index].nStartBlock = 10240+(i*512); 
		fseek(f, (*dir).files[index].nStartBlock, SEEK_SET);
		fwrite(buf, sizeof(char), strlen(buf), f);
		fclose(f);
	}
	else
	{
		fseek(f, (*dir).files[index].nStartBlock, SEEK_SET);
		fwrite(buf, sizeof(char), strlen(buf), f);
		fclose(f);
	}
  	return size;
}

/*
 * Called whenever the system wants to know the file attributes, including
 * simply whether the file exists or not. 
 *
 * man -s 2 stat will show the fields of a stat structure
 */
static int cs1550_getattr(const char *path, struct stat *stbuf)
{
	int res = 0;
	int index; 
	memset(stbuf, 0, sizeof(struct stat));
   	char directory[MAX_FILENAME+1];
   	char filename[MAX_FILENAME+1];
   	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
   	cs1550_directory_entry dir;
	
	//is path the root dir?
	if (strcmp(path, "/") == 0) 
	{
		stbuf->st_mode = S_IFDIR | 0755;
		stbuf->st_nlink = 2;
	} 
	else 
	{
		int i = 0;
		sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension);
		while(1)
		{
			index = getIndexOfDir(&dir, i);
			if(strcmp(directory, dir.dname)==0)
				break;
			if(index == -1)
				break;
			i++;
		}

		if(index == -1 || (filename[0] != '\0'))//dir not found OR we have a file
		{
			if(index == -1)
				return -ENOENT;
			for(i = 0; i < dir.nFiles; i++)
			{

				if( (strcmp(dir.files[i].fname,filename) == 0) && (strcmp(dir.files[i].fext,extension) == 0))//if file exists
				{
					stbuf->st_mode = S_IFREG | 0666; 
					stbuf->st_nlink = 1; //file links
					stbuf->st_size = dir.files[i].fsize; //file size - make sure you replace with real size!
					return 0;
				}
			}
			return -ENOENT;

		}
		else
		{
			stbuf->st_mode = S_IFDIR | 0755;
			stbuf->st_nlink = 2;
			res = 0;
		}
		
	}
	return res;
}

/* 
 * Called whenever the contents of a directory are desired. Could be from an 'ls'
 * or could even be when a user hits TAB to do autocompletion
 */
static int cs1550_readdir(const char *path, void *buf, fuse_fill_dir_t filler,
			 off_t offset, struct fuse_file_info *fi)
{
	(void) offset;
	(void) fi;
	int index = 0;
	int i = 0;
	char directory[MAX_FILENAME+1];
	char filename[MAX_FILENAME+1];
	char extension[MAX_EXTENSION+1];
	cs1550_directory_entry dir;
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension);
	//This line assumes we have no subdirectories, need to change
	if (strcmp(path, "/") != 0)
	{
		if(directory!=NULL)
		{
			while(1)
			{
				index = getIndexOfDir(&dir, i);
				if(strcmp(directory, dir.dname)==0)
					break;
				if(index == -1)
					break;
				i++;
			}
			filler(buf, ".", NULL,0);
			filler(buf, "..", NULL, 0);
			for(i = 0; i < dir.nFiles; i++)
			{
				char printfiles[MAX_FILENAME + MAX_EXTENSION +1];
				strcpy(printfiles, dir.files[i].fname);
				if(strlen(dir.files[i].fext)>0)
				{
					strcat(printfiles, ".");
					strcat(printfiles, dir.files[i].fext);
				}
				filler(buf, printfiles, NULL, 0);
			}
		}
		else
			return -ENOENT;
	}
	else
	{
		filler(buf, ".", NULL,0);
		filler(buf, "..", NULL, 0);
		while(index != -1)
		{
			index = getIndexOfDir(&dir, i);
			if(index != -1)
				filler(buf, dir.dname, NULL, 0);
			i++;
		}
	}
	return 0;
}

/* 
 * Creates a directory. We can ignore mode since we're not dealing with
 * permissions, as long as getattr returns appropriate ones for us.
 */
static int cs1550_mkdir(const char *path, mode_t mode)
{
	(void) mode;
	cs1550_directory_entry dir;
	int i = 0;
	int index;
	char directory[MAX_FILENAME+1];
	char filename[MAX_FILENAME+1];
	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension);

	if(directory == NULL || directory[0] == '\0' || strlen(filename) > 0) 
		return -EPERM;
	else
	{
		while(1)
		{
			index = getIndexOfDir(&dir, i);
			if(strcmp(directory, dir.dname)==0)
				break;
			if(index == -1)
				break;
			i++;
		}
		if(index == -1)
		{
			if(strlen(directory) <= MAX_FILENAME)
			{
				memset(&dir, 0, sizeof(struct cs1550_directory_entry));
				strcpy(dir.dname, directory);
				dir.nFiles = 0;
				FILE *f = fopen(".directories", "ab");
				fwrite(&dir, sizeof(cs1550_directory_entry), 1, f);
				fclose(f);
			}
			else
				return -ENAMETOOLONG;
		}
		else
			return -EEXIST;
	}

	return 0;
}

/* 
 * Removes a directory.
 */
static int cs1550_rmdir(const char *path)
{
	(void) path;
    return 0;
}

/* 
 * Does the actual creation of a file. Mode and dev can be ignored.
 *
 */
static int cs1550_mknod(const char *path, mode_t mode, dev_t dev)
{
	(void) mode;
	(void) dev;
	(void) path;
	char directory[MAX_FILENAME+1];
   	char filename[MAX_FILENAME+1];
   	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	cs1550_directory_entry dir;
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension);
	int index;
	int i = 0;
	int res = 0;
	if(directory==NULL || strlen(filename) < 1) //-EPERM if the file is trying to be created in the root dir
		return -EPERM;
	else//we are not in root
	{
		if(strlen(filename) > MAX_FILENAME || strlen(extension) > MAX_EXTENSION)
			return -ENAMETOOLONG;
		while(1)//while helps us get the index of the directory we want.. breaks the loop when we find the match or if dir doesnt exist
		{
			index = getIndexOfDir(&dir, i);
			if(strcmp(directory, dir.dname)==0)
				break;
			if(index == -1)
				break;
			i++;
		}
		int temp = fileExists(filename, extension, &dir);
		if(temp == -1)//helper function which tells is if the file exists (returns -1 if it doesnt)
		{
			strcpy(dir.files[dir.nFiles].fname, filename);
			strcpy(dir.files[dir.nFiles].fext, extension);
			dir.files[dir.nFiles].fsize = 0;
			dir.nFiles++;
			addFileToDotDir(&dir, index);
			res = 0;
		}
		else
			return -EEXIST;
	}
	return res;
}


/*
 * Deletes a file
 */
static int cs1550_unlink(const char *path)
{
    (void) path;
    int i = 0;
    int index;
    char directory[MAX_FILENAME+1];
	char filename[MAX_FILENAME+1];
	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension); 
	cs1550_directory_entry dir;
	if(directory !=NULL && strlen(filename) < 1)
		return -EISDIR;// if the path is a directory
	while(1)//while helps us get the index of the directory we want.. breaks the loop when we find the match or if dir doesnt exist
	{
		index = getIndexOfDir(&dir, i);
		if(strcmp(directory, dir.dname)==0)
			break;
		if(index == -1)
			break;
		i++;
	}
	int temp = fileExists(filename, extension, &dir);
	if(temp == -1)
		return -ENOENT;// if the file is not found
	else
	{
		for(i = 0; i <= dir.nFiles; i++)
		{
			char printfiles[MAX_FILENAME + MAX_EXTENSION +1];
			char incomingFileName[MAX_FILENAME + MAX_EXTENSION +1];
			strcpy(incomingFileName, filename);
			strcpy(printfiles, dir.files[i].fname);
			if(strlen(dir.files[i].fext)>0)
			{
				strcat(incomingFileName, ".");
				strcat(incomingFileName, extension);
				strcat(printfiles, ".");
				strcat(printfiles, dir.files[i].fext);

			}
			if(strcmp(printfiles, incomingFileName ) == 0 )
			{
				char c = '\0';
				FILE* f = fopen(".disk", "rb+");
				int k = ((dir.files[i].nStartBlock / 512) % 20);
				fseek(f, k, SEEK_SET);
				fputs( &c, f);
				fclose(f);
				dir.files[i] = dir.files[dir.nFiles - 1]; 
				dir.nFiles--;
				addFileToDotDir(&dir, index);

			}
		}		
	}
    return 0;
}
/* 
 * Read size bytes from file into buf starting from offset
 *
 */
static int cs1550_read(const char *path, char *buf, size_t size, off_t offset,
			  struct fuse_file_info *fi)
{
	(void) buf;
	(void) offset;
	(void) fi;
	(void) path;
	int index;
	char directory[MAX_FILENAME+1];
	char filename[MAX_FILENAME+1];
	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension); 
	cs1550_directory_entry dir;
	if(directory !=NULL && strlen(filename) < 1)
		return -EISDIR;// if the path is a directory
	if(size<=0)
		return -1;
	if(offset > size)
		return -1;
	if(directory!=NULL)
	{
		if(strlen(filename) <= MAX_FILENAME && strlen(filename) > 0)
		{
			if(strlen(extension) <= MAX_EXTENSION)
			{
				int i = 0;
				while(1)
				{
					index = getIndexOfDir(&dir, i);
					if(strcmp(directory, dir.dname)==0)
						break;
					if(index == -1)
						break;
					i++;
				}
				for(i = 0; i < dir.nFiles; i++)
				{
					char printfiles[MAX_FILENAME + MAX_EXTENSION +1];
					char incomingFileName[MAX_FILENAME + MAX_EXTENSION +1];
					strcpy(incomingFileName, filename);
					strcpy(printfiles, dir.files[i].fname);
					if(strlen(dir.files[i].fext)>0)
					{
						strcat(incomingFileName, ".");
						strcat(incomingFileName, extension);
						strcat(printfiles, ".");
						strcat(printfiles, dir.files[i].fext);
					}
					if(strcmp(printfiles, incomingFileName ) ==0)
					{
						int returnVal;
						int l = dir.files[i].fsize;
						char readChar[l+1];
						FILE* f = fopen(".disk", "rb+");
						int k = (dir.files[i].nStartBlock);
						fseek(f, k, SEEK_SET);
						returnVal =  fread(&readChar, sizeof(char), dir.files[i].fsize, f);
						fclose(f);
						l = l + offset;
						for(i = 0; i < strlen(readChar); i++)
						{
							*buf = readChar[i];
							buf++; 					
						}
						return returnVal;
					}
				}
			}
		}
	}
	//read in data
	//set size and return, or error
	return size;
}

/* 
 * Write size bytes from buf into file starting from offset
 *
 */
static int cs1550_write(const char *path, const char *buf, size_t size, 
			  off_t offset, struct fuse_file_info *fi)
{
	(void) buf;
	(void) offset;
	(void) fi;
	(void) path;
	int index;
	char directory[MAX_FILENAME+1];
	char filename[MAX_FILENAME+1];
	char extension[MAX_EXTENSION+1];
	memset(directory, 0, MAX_FILENAME + 1);
	memset(filename, 0, MAX_FILENAME + 1);
	memset(extension, 0, MAX_EXTENSION + 1);
	cs1550_directory_entry dir;
	cs1550_disk_block writeblock;
	memset(&writeblock, 0, sizeof(cs1550_disk_block));
	sscanf(path, "/%[^/]/%[^.].%s", directory, filename, extension); 
	if(size<=0)
		return -1;
	if(offset > size)
		return -EFBIG;
	if(directory!=NULL)
	{
		if(strlen(filename) <= MAX_FILENAME && strlen(filename) > 0)
		{
			if(strlen(extension) <= MAX_EXTENSION)
			{
				int i = 0;
				while(1)
				{
					index = getIndexOfDir(&dir, i);
					if(strcmp(directory, dir.dname)==0)
						break;
					if(index == -1)
						break;
					i++;
				}
				for(i = 0; i <= dir.nFiles; i++)
				{
					char printfiles[MAX_FILENAME + MAX_EXTENSION +1];
					char incomingFileName[MAX_FILENAME + MAX_EXTENSION +1];
					strcpy(incomingFileName, filename);
					strcpy(printfiles, dir.files[i].fname);
					if(strlen(dir.files[i].fext)>0)
					{
						strcat(incomingFileName, ".");
						strcat(incomingFileName, extension);
						strcat(printfiles, ".");
						strcat(printfiles, dir.files[i].fext);
					}
					if(strcmp(printfiles, incomingFileName ) ==0)
					{
						size = write(buf, size, offset, i, &dir);//size gets set inside call to write
						addFileToDotDir(&dir, index);
					}
				}
			}
		}
	}
	//check to make sure path exists
	//check that size is > 0
	//check that offset is <= to the file size
	//write data
	//set size (should be same as input) and return, or error

	return size;
}

/******************************************************************************
 *
 *  DO NOT MODIFY ANYTHING BELOW THIS LINE
 *
 *****************************************************************************/

/*
 * truncate is called when a new file is created (with a 0 size) or when an
 * existing file is made shorter. We're not handling deleting files or 
 * truncating existing ones, so all we need to do here is to initialize
 * the appropriate directory entry.
 *
 */
static int cs1550_truncate(const char *path, off_t size)
{
	(void) path;
	(void) size;

    return 0;
}


/* 
 * Called when we open a file
 *
 */
static int cs1550_open(const char *path, struct fuse_file_info *fi)
{
	(void) path;
	(void) fi;
    /*
        //if we can't find the desired file, return an error
        return -ENOENT;
    */

    //It's not really necessary for this project to anything in open

    /* We're not going to worry about permissions for this project, but 
	   if we were and we don't have them to the file we should return an error
        return -EACCES;
    */

    return 0; //success!
}

/*
 * Called when close is called on a file descriptor, but because it might
 * have been dup'ed, this isn't a guarantee we won't ever need the file 
 * again. For us, return success simply to avoid the unimplemented error
 * in the debug log.
 */
static int cs1550_flush (const char *path , struct fuse_file_info *fi)
{
	(void) path;
	(void) fi;

	return 0; //success!
}


//register our new functions as the implementations of the syscalls
static struct fuse_operations hello_oper = {
    .getattr	= cs1550_getattr,
    .readdir	= cs1550_readdir,
    .mkdir	= cs1550_mkdir,
	.rmdir = cs1550_rmdir,
    .read	= cs1550_read,
    .write	= cs1550_write,
	.mknod	= cs1550_mknod,
	.unlink = cs1550_unlink,
	.truncate = cs1550_truncate,
	.flush = cs1550_flush,
	.open	= cs1550_open,
};

//Don't change this.
int main(int argc, char *argv[])
{
	return fuse_main(argc, argv, &hello_oper, NULL);
}
Status API Training Shop Blog About
© 2015 GitHub, Inc. Terms Privacy Security Contact
