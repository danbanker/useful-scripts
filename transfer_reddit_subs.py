'''
Subscribes to a list of subreddits via a multireddit link, raw comma-delimited list, or credentials

USAGE:

Must create a Script app in https://www.reddit.com/prefs/apps/ of the new user with URI as http://localhost:8080

The CLIENT_ID is at the top left of the app and the CLIENT_SECRET is the next code down

Best to put the CLIENT_ID, CLIENT_SECRET, TO_USERNAME, TO_PASSWORD in environmental vars

Authentication to the originating, "From", account are achieved via oAuth through prompted instructions

python transfer_reddit_subs.py --from_username "AtheistMessiah" --from_refresh_token "add_this_if_you_have_it_from_a_previous_run"

'''

import argparse
import praw
import os
import sys
import socket
import random
from praw.exceptions import RedditAPIException


parser = argparse.ArgumentParser()
parser.add_argument('-u','-m', '-l', '--list', '--url', '--multireddit', dest='input_list',
                    help='Multireddit URL from (https://old.reddit.com/subreddits/) or comma-delimited list', required=False)
parser.add_argument('-c', '--client_id', dest='client_id',
                    help='From https://www.reddit.com/prefs/apps/ (Can add as eviron var CLIENT_ID)',
                    required=False)
parser.add_argument('-s','--secret', '--client_secret', dest='client_secret',
                    help='From https://www.reddit.com/prefs/apps/ (Can add as eviron var CLIENT_SECRET)',
                    required=False)
parser.add_argument('-a','--agent', '--user_agent', dest='user_agent',
                    help='Reddit username or some other unique identifier',
                    required=False)
parser.add_argument('--fu', '--ou', '--old_username','--from_username', dest='from_username',
                     help='old reddit username (optional if --url is used)', required=False)
parser.add_argument('--ft', '--from_refresh_token', dest='from_refresh_token',
                    help='the oAuth authorization id of the "From account" if known', required=False)
parser.add_argument('--tu', '--nu', '--new_username','--to_username', dest='to_username',
                    help='new/to Reddit username', required=False)
parser.add_argument('--tp', '--np', '--new_password','--to_password', dest='to_password',
                    help='new/to Reddit user password', required=False)
args = parser.parse_args()

def coalesce(*arg):
  for el in arg:
    if el is not None:
      return el
  return None

# As per https://praw.readthedocs.io/en/latest/tutorials/refresh_token.html
def receive_connection():
    """Wait for and then return a connected socket..

    Opens a TCP connection on port 8080, and waits for a single client.

    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("localhost", 8080))
    server.listen(1)
    client = server.accept()[0]
    server.close()
    return client

def send_message(client, message):
    """Send message to client and close the connection."""
    print(message)
    client.send("HTTP/1.1 200 OK\r\n\r\n{}".format(message).encode("utf-8"))
    client.close()

def main():

    client_id = coalesce(args.client_id, os.getenv('CLIENT_ID'))
    client_secret = coalesce(args.client_id, os.getenv('CLIENT_SECRET'))
    from_username = coalesce(args.from_username, os.getenv('FROM_USERNAME'))
    to_username = coalesce(args.to_username, os.getenv('TO_USERNAME'))
    user_agent = coalesce(args.user_agent, to_username)
    to_password = coalesce(args.to_password, os.getenv('TO_PASSWORD'))
    from_refresh_token = coalesce(args.from_refresh_token, os.getenv('FROM_REFRESH_TOKEN'))
    input_list = args.input_list

    if not [x for x in (client_id, client_secret, user_agent, to_username, to_password) if x is None] and \
            (from_username or input_list):
        pass
    else:
        raise NameError('ERROR: Not all required parameters were input!')

    if input_list:
        if '/r/' in input_list:
            subreddits = input_list.split('/r/')[1].split('+')
        else:
            subreddits = [x.strip() for x in input_list.split(',')]
    else:
        # Assume that the app is not yet authorized by the "From" user unless directed
        if from_refresh_token:
            from_user_session = praw.Reddit(client_id=client_id,
                                 client_secret=client_secret,
                                 refresh_token=from_refresh_token,
                                 user_agent=user_agent)
            print(from_user_session.auth.scopes())
        else:
            from_user_session = praw.Reddit(client_id=client_id,
                                 client_secret=client_secret,
                                 user_agent=user_agent,
                                 redirect_uri='http://localhost:8080')

            scopes = ['mysubreddits', 'identity']
            state = str(random.randint(0, 65000))
            url = from_user_session.auth.url(scopes, state, 'permanent')
            print("Open this url in your browser: " + url)
            sys.stdout.flush()

            client = receive_connection()
            data = client.recv(1024).decode("utf-8")
            param_tokens = data.split(" ", 2)[1].split("?", 1)[1].split("&")
            params = {
                key: value for (key, value) in [token.split("=") for token in param_tokens]
            }

            if state != params["state"]:
                send_message(
                    client,
                    "State mismatch. Expected: {} Received: {}".format(state, params["state"]),
                )
                return 1
            elif "error" in params:
                send_message(client, params["error"])
                return 1

            refresh_token = from_user_session.auth.authorize(params["code"])
            send_message(client, "Refresh token: {}".format(refresh_token))

        # This will fail if credentials are incorrect, app is not authorized, or scopes are wrong
        try:
            print('oAuth into user {} successful!'.format(from_user_session.user.me()))
        except RedditAPIException as exception:
            print(exception.items[0].error_type)

        subreddits = []
        for subreddit in from_user_session.user.subreddits(limit=None):
              subreddits.append(subreddit.display_name)

    # login to new user
    to_user_session = praw.Reddit(client_id=client_id,
                                       client_secret=client_secret,
                                       user_agent=user_agent,
                                        username=to_username,
                                       password=to_password)

    # This will fail if credentials are incorrect
    try:
        print(to_user_session.user.me())
    except RedditAPIException as exception:
        print(exception.items[0].error_type)

    success_counter = 0
    fail_counter = 0
    total_subreddits = len(subreddits)
    for sub_counter, sub in enumerate(subreddits, start=1):
        try:
            to_user_session.subreddit(sub).subscribe(other_subreddits=None)
            success_counter += 1
            print("({} of {}) (Fails: {}) -- Subscribed {} to {}".format(sub_counter, total_subreddits, fail_counter, to_username, sub))
        except:
            fail_counter += 1
            print("({} of {}) (Fails: {}) -- Error subscribing {} to {}".format(sub_counter, total_subreddits, fail_counter, to_username, sub))

    return {'success_counter': success_counter, 'fail_counter': fail_counter,
            'total_subreddits': total_subreddits, 'to_username': to_username,
            'from_username': from_username, 'subreddits': subreddits}

if __name__ == '__main__':
    main()
    print('Script complete!')