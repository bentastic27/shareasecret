# Setup

1. Change the `app.config['SECRET_KEY']` string as that will be used be used for various things like CSRF with WTF forms. The longer and more random the better.
2. If `secret.db` does not exist you can create it by running `sqlite3 secret.db < schema.sql` from the command line in the directory that this app is installed in.
3. Setup cronjob to run the `dbclean.py` script nightly. This will be the piece responsible for clearing old secrets after 7 days.
4. Install the dependencies with `pip install -r requirements.txt`
5. Deployment should be similar to any of the options outlined at http://flask.pocoo.org/docs/0.10/deploying/

# License

Attribution-ShareAlike 4.0 International

http://creativecommons.org/licenses/by-sa/4.0/

# Author

Ben Healey at http://www.beansnet.net/

Inspired by https://github.com/onetimesecret/onetimesecret