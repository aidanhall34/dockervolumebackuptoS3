#!/usr/bin/python3
import shutil
import datetime
import os
import argparse
import boto3

def make_backups(config_file, docker_volumes):
    for volume in docker_volumes:
        path = '/var/lib/docker/volumes/' + volume
        output_filename = f"/tmp/{volume}_{datetime.datetime.now().strftime('%d_%m_%Y')}"
        print(f"Creating backup file {output_filename}.zip from {path}")
        shutil.make_archive(output_filename, 'zip', path)
        # S3 uploading started
        s3 = make_session(config_file)
        try:
            s3.upload_file(f"{output_filename}.zip", f"{output_filename}.zip")
        except Exception as e:
            print(f"Uploading the backup failed for the following reason:\n{e}")
            return "Backup failed"
        print(f"Backup succesfully uploaded volume {volume} to your S3 bucket, sitesandservicesbackup")
    # Remove temporary backup from local
    os.remove(output_filename + '.zip') 
    return "Backup complete"

def restore_backups(config_file, docker_volumes, date):
    for volume in docker_volumes:
        volumepath = f"/var/lib/docker/volumes/{volume}"
        path = f"/tmp/{volume}{date}.zip" 
        print(f"Restoring {volume} to {volumepath}")
        s3 = make_session(config_file)
        with open(f"/tmp/{volume}{date}.zip", 'wb') as zipfile:
            try:
                s3.download_file(f"/tmp/{volume}_{date}.zip", f"/tmp/{volume}_{date}.zip")
            except Exception as e:
                print(f"Downloading the restore failed for the following reason:\n{e}")
                return "Downloading the restore failed"
            shutil.unpack_archive(f"/tmp/{volume}_{date}.zip", volumepath, 'zip')
            os.remove(f"/tmp/{volume}_{date}.zip")
        print("Successfully restored the volume")
        return "Restore complete"

def make_session(configfile):
    with open('/root/S3.config', 'r')as creds:
    # Make this better, fuck spliting its dumb
        creds = creds.readlines()
        Access_key_ID = creds[0].strip().split('=')[1]
        Secret_access_key = creds[1].strip().split('=')[1]
        Bucketname = creds[2].strip().split('=')[1]
    # Boto Session
    session = boto3.Session(
        aws_access_key_id=Access_key_ID,
        aws_secret_access_key=Secret_access_key)
    s3 = session.resource('s3')
    s3 = s3.Bucket(Bucketname)
    return s3

args = argparse.ArgumentParser()
args.add_argument('-b','--backup',help='A list of docker volumes you wish to backup', action='store_true')
args.add_argument('-r','--restore',help="A list of docker volumes you wish to restore",  action='store_true')
args.add_argument('-v','--volumes',help='A list of docker volumes you wish to interact with', nargs="+")
args.add_argument('-d', '--date', help='Restore a backup taken on a spefic date' )
args.add_argument('-c', '--config', help='Speficy a config file location')
args = args.parse_args()

def main():
    if args.config == None:
        print('Please provide a config file')
        exit(1)
    if args.volumes == None:
        print('Please speficy a volume/s name/s')
        exit(1)
    if args.restore and args.backup or args.restore != True and args.backup != True:
        print('Please speficy only one operation')
        exit(1)
    if args.restore and args.date == None:
        print('Please provide a date for the backup in %D_%M_Y% format')
        exit(1) 
    if args.restore:
        print(restore_backups(args.config, args.volumes, args.date))
    else:
        print(make_backups(args.config, args.volumes))

if __name__ == '__main__':
    main()
