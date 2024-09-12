import sqlite3
from github import Github
from github import Auth 
import os
import csv
import datetime
import logging
import sys
import uuid

SESSION_ID = uuid.uuid4()
ONE_MONTH_AGO = (datetime.datetime.now() - datetime.timedelta(days=30)).replace(tzinfo=datetime.timezone.utc)

## Logging ##
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create log directory if it doesn't exist
if not os.path.exists('./logs'):
    os.makedirs('./logs')
    
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(filename=f"./logs/{SESSION_ID}.log")

console_handler.setLevel(logging.INFO)
file_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s")
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)


def init_db():
    logger.debug('initializing database')

    # setup database
    conn = sqlite3.connect('./gh.db')
    cursor = conn.cursor()

    # create table if doesn't exist
    create_table_query = '''
                   CREATE TABLE IF NOT EXISTS pull_requests (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       session_id TEXT,
                       source TEXT,
                       repo TEXT,
                       user TEXT,
                       pr_number INTEGER,
                       state TEXT,
                       created_at DATETIME,
                       merged_at DATETIME,
                       assignee TEXT,
                       merged_by TEXT,
                       created_at_ts DATETIME,
                       updated_at_ts DATETIME
                       );
                   '''
    cursor.execute(create_table_query)
    logger.debug(f"executed query: {create_table_query}")
    # create index if doesn't exist for session_id
    indexes_queries = [
                   """CREATE INDEX IF NOT EXISTS pull_requests_session_id ON
                   pull_requests (session_id);""",
                   """CREATE INDEX IF NOT EXISTS pull_requests_repo ON
                   pull_requests (repo);""",
                   """CREATE INDEX IF NOT EXISTS pull_requests_merged_by ON
                   pull_requests (merged_by);""",
                   """CREATE INDEX IF NOT EXISTS pull_requests_merged_at ON
                   pull_requests (merged_at);"""]
    [cursor.execute(q) for q in indexes_queries]
    logger.debug(f"executed queries: {', '.join(indexes_queries)}")

    return conn, cursor


def save_record(record, conn, cursor):
    query = """
    INSERT INTO pull_requests (session_id, source, repo, user, pr_number, state,
                               created_at, merged_at, assignee, merged_by,
                               created_at_ts, updated_at_ts)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""

    values = (str(SESSION_ID), 'script', record['repo'], record['user'],
              record['pr_number'], record['state'], record['created_at'],
              record['merged_at'], record['assignee'], record['merged_by'],
              datetime.datetime.now(tz=datetime.timezone.utc),
              datetime.datetime.now(tz=datetime.timezone.utc))
    cursor.execute(query, values)
    conn.commit()
    logger.debug(f"executed query: {query}, values: {values}")

 

## PR Program ##
def ingest_merged_pullrequests(prs, repo=None, from_date=ONE_MONTH_AGO, include_not_merged=False, cursor=None):
    for pr in prs:
        if include_not_merged == False and pr.is_merged() == False:
            continue
        if pr.merged_at < from_date:
            continue

        if repo is not None and pr_stored(pr.number, repo, cursor) == True:
            logger.debug(f"skipping {pr.number} for {repo} already stored in database")
            continue

        yield parse_pull_request(pr)

def pr_stored(pr_number, repo, cursor):
    query = """SELECT COUNT(*) FROM pull_requests WHERE pr_number = ? AND repo = ?"""
    cursor.execute(query, (pr_number, repo))

    return cursor.fetchone()[0] > 0

def parse_pull_request(pr):
    user = pr.user.login
    state = pr.state
    created_at = pr.created_at
    merged_at = pr.merged_at
    assignee = ','.join([a.login for a in pr.assignees]) if pr.assignees is not None else 'NF'
    merged_by = pr.merged_by.login
    pr_number = pr.number

    return {
            'user':user,
            'pr_number': pr_number,
            'state':state,
            'created_at': created_at,
            'merged_at':merged_at,
            'assignee':assignee,
            'merged_by':merged_by,
            }

def usage():
    message = """
    Usage: python pr.py <from_date> <organization>

    Example: python pr.py "2021-01-01" "MyOrg"
    """

    print(message)

## MAIN ##

logger.info('Starting')

logger.info(f"session id: {SESSION_ID}")
logger.info(f"log file: {file_handler.baseFilename}")

# initialize database
conn, cursor = init_db()
logger.debug("database initialized")

logger.debug("parsing script arguments for date range and organization")
from_date = ONE_MONTH_AGO
org = 'NF'

if len(sys.argv) != 3:
    usage()
    logger.error(f"Faltan argumentos... {len(sys.argv)}, sys.argv: {sys.argv}")
    exit(1)

if len(sys.argv) > 1:
    from_date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d')
    from_date = from_date.replace(tzinfo=datetime.timezone.utc)

    org = sys.argv[2]


logger.debug('authenticating with githubs token using GH_TOKEN environment variable')
# Get the token from the environment
gh_token = os.getenv('GH_TOKEN', 'asdf')

if gh_token == 'asdf':
    logger.error('GH_TOKEN environment variable not set')
    exit(1)

# Create authentication object
auth = Auth.Token(gh_token)

g = Github(auth=auth,)

logger.info('authenticated')

# organization
gh_org = g.get_organization(org)

# organization members
members = gh_org.get_members()
logger.info(f"organization {gh_org.name} has {members.totalCount} members fetched")


# repositories sorted by most recently updated
logger.debug("fetching repositories")
repos = gh_org.get_repos(type='member', sort='updated', direction='desc')
logger.info(f"fetched {repos.totalCount} repositories")


# create a key value structure for members vs merged pull requests

# for each repository we wan to get the pull requests merged in last month

data = [[r.name, r.get_pulls(state='closed', sort='updated', direction='desc')] for r in repos]

logger.debug("getting prs closed, sorted by most recently updated")

logger.info(f"fetching github data from {from_date.strftime('%Y-%m-%d')} to {datetime.datetime.now().strftime('%Y-%m-%d')}")

results = {}
for repo, pulls in data:
    if pulls.totalCount == 0:
        logger.debug(f"no pull requests found for {repo}")
        continue

    logger.debug(f"repo: {repo}, total pull requests: {pulls.totalCount}")

    # ingest pull requests data
    results[repo] = ingest_merged_pullrequests(pulls, repo=repo, from_date=from_date, include_not_merged=False, cursor=cursor)

# csv output

logger.info('Writing to csv')

fieldnames = ['repo', 'user', 'pr_number', 'state', 'created_at', 'merged_at', 'assignee', 'merged_by']

csv_file = './pull_requests_results.csv'

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for repo, items in results.items():
        for i in items:
            [writer.writerow({'repo':repo, **i})]
            [save_record({'repo':repo, **i}, conn, cursor)]


logger.info(f"csv written to {csv_file}")
logger.debug('closing database connection')
conn.close()

print(f"logger generated on: logs/{SESSION_ID} directory")
