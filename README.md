# dockervolumebackuptoS3
Backs up Docker container volumes and uploads them to an AWS s3 bucket

Firstly, you will need to create an AWS account with programattic access to your s3 buckets.

The create a S3.config file like the one shown in this folder and place it somewhere secure (I use /root).
Run the script has the following arguments:
```
'-b','--backup'

'-r','--restore'

'-v','--volumes'

'-d', '--date'

'-c', '--config'
```

Use -c to point at config file the S3.conf you created earlier

Either choose to backup or restore from S3 with -b or -r

Specify the volumes you wish to target with -r. This should be provided as a list with spaces, see cronvolumebackup.example for referance.

If you specify restore, you must provide a date with -d in %d%d_%m%m_%Y%Y%Y%Y format

## Personal setup
I run this as a cron job. After creating and setting up the config file, I edit the cronvolumebackup.example to include the volumnes I want backed up.
After adding those I put it into /etc/cron.d/ and reload cron. I have my s3 bucket set up to retain backups for 30 days.
