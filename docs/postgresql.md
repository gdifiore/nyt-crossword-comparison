# PostgreSQL Linux Tutorial (only for running locally)

`sudo apt install postgresql`

In `/etc/postgresql/*/main/postgresql.conf`, locate the line: `#listen_addresses = ‘localhost’` and change it to *:

## Switch from Peer to Password Authentication: 

1. Update the PostgreSQL configuration file (pg_hba.conf) to use md5 authentication instead of peer for local connections. Here's how:

    Locate the pg_hba.conf file:

    `sudo find / -name "pg_hba.conf"`

2. Open it in an editor (you may need sudo):

    `sudo nano /path/to/pg_hba.conf`

    Look for a line like this:

    `local   all             postgres                                peer`

    Change peer to md5:

    `local   all             postgres                                md5`

    Save the file and reload PostgreSQL:

    `sudo systemctl restart postgresql`
    NOTE: if you're using WSL, the command is `sudo service postgresql restart`

3. Set a Password for the PostgreSQL User: If you haven't already set a password for the user, do so now:

```
sudo -u postgres psql
\password postgres
```

Enter the password you used in the .env file.

Verify Connection: Test the connection with the psql command-line tool to ensure it works:

`psql -h localhost -U your_database_user -d your_database_name`