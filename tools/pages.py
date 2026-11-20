#!/usr/bin/env python3
"""Writes the database pages (/postgresql-client/ …), the comparison pages (/alternatives/…)
and the shared footer of index.html. The pages are plain HTML committed to the repo, so the site
still has no build step: run this only after changing the content below.

    python3 tools/pages.py

Facts about NavQL come from the app's README. Facts about other products come from their public
websites, read on the date in CHECKED; keep them conservative and re-check before changing them.
"""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = 'https://navql.com'
CHECKED = '19 November 2026'
LASTMOD = '2026-11-19'

# ---------------------------------------------------------------------------------------------
# Screenshots (all real NavQL screens, in assets/shots)
SHOTS = {
    'table': 'The customers table of a PostgreSQL store database in the NavQL data grid, 1,200 rows',
    'query': 'Query editor with a SELECT grouping revenue by city and the result below',
    'structure': 'Structure of the orders table: columns, types, indexes and foreign keys',
    'diagram': 'Database diagram of a store schema: 15 tables connected by their foreign keys',
    'diagram-focus': 'The orders table selected in the diagram, with its related tables highlighted and the rest faded',
    'connections': 'NavQL connection list for the Store project: PostgreSQL, Redis, SQL Server and MongoDB connections, each with its own color and tag',
    'redis': 'Redis keys with the session prefix in a grid: key, type, TTL, size and value',
    'value': 'Data grid of the orders table with the JSON of a cell shown as a tree in the side panel',
}

# Which database each screenshot shows, for the caption under it
SHOT_DB = {'redis': 'Redis', 'connections': None}

# ---------------------------------------------------------------------------------------------
# Database pages
#
# Each card is (title, html). "notyet" lists what NavQL does not do there yet: honest pages rank
# better with people than pages that promise everything.

SQL_GRID = ('Edit rows, then commit once',
            'Change cells, insert, duplicate and delete rows in the grid. Every change stays pending '
            '(yellow, green, red) until you press <code>⌘S</code>; <em>Preview</em> shows the SQL first and the '
            'whole batch commits in one transaction.')
RELATED = ('Related rows, as a tree',
           'Open a row and see everything linked to it by foreign keys: the rows it points to and, for each '
           'table that points back, how many rows and the first ones. Each row opens its own relationships, as '
           'many levels deep as you like.')
BUILDER = ('Visual query builder',
           'Pick a table, add the tables linked to it by foreign keys (or join any table with your own '
           '<code>ON</code>), filters, aggregates, <code>HAVING</code> and calculated columns. The SQL is written '
           'live, and you can save the builder or open the SQL in an editor tab.')
ALTER = ('Edit the structure',
         'Columns, indexes, foreign keys and the DDL of every table. Edit columns in place and NavQL applies the '
         'change as <code>ALTER TABLE</code>, after showing you the statement.')
DIAGRAM = ('Database diagram',
           'One click draws every table and the foreign keys between them, laid out automatically. Click a table '
           'to highlight what it touches; export the diagram as PNG or SVG.')
EDITOR = ('SQL editor that knows your schema',
          'Autocomplete for tables and columns, <code>⌘↵</code> runs the statement under the cursor, '
          '<code>⌘I</code> formats, and several result sets open in tabs. Saved queries and history are kept per '
          'connection.')
SSH = ('SSH tunnel and SSL',
       'Reach databases on private networks through a built-in SSH tunnel (password or private key), with SSL/TLS. '
       'Passwords and keys are encrypted on your computer.')
READONLY_TX = lambda db: ('Read only that really is',
                          f'Mark a connection <em>Read only</em> and NavQL accepts only reading statements, then runs '
                          f'them inside a <code>READ ONLY</code> transaction on {db}, so a CTE with '
                          f'<code>DELETE</code> or a function that writes is refused too.')
AI = ('AI assistant, optional',
      '<code>⌘J</code> writes a query from a sentence, <em>Explain</em> explains one and <em>Fix with AI</em> '
      'proposes a fix when it fails. It uses your own Anthropic key and sends the structure of the database and '
      'the editor text, never the data in your tables.')
EXPORT = ('Export and import',
          'Export a page or a whole table to CSV, JSON or SQL. Import a CSV and its rows arrive as pending changes '
          'you review before saving.')


def activity_pg(name='PostgreSQL'):
    return ('Activity: sessions, top queries, health',
            f'Every session on the {name} server with its query, state and wait, including who blocks whom. Cancel a '
            'query or end a session (<code>pg_cancel_backend</code>, <code>pg_terminate_backend</code>). Top queries '
            'come from <code>pg_stat_statements</code>.')


def backup_pg():
    return ('Backups with pg_dump',
            'Back up a whole database in one click with <code>pg_dump --format=custom</code>. It runs in the '
            'background, streams straight to a file, works through the SSH tunnel and shows progress. Restore with '
            '<code>pg_restore</code>.')


DATABASES = [
    dict(slug='postgresql-client', name='PostgreSQL', kind='core', shot='table',
         title='PostgreSQL client for Mac, Windows and Linux — NavQL',
         desc='Free PostgreSQL client for Mac, Windows and Linux: edit rows with one commit, follow foreign keys, watch sessions and top queries, back up with pg_dump.',
         h1='A free PostgreSQL client that <span class="hl">follows the data.</span>',
         lead='Browse and edit tables, follow foreign keys to the rows they point to, watch what the server is doing '
              'and back it up, all in one desktop app.',
         facts=[('PostgreSQL', 'and compatible servers'), ('pg_dump backups', 'custom format, in the background'),
                ('READ ONLY', 'transactions for read-only'), ('Free', 'macOS · Windows · Linux')],
         cards=[SQL_GRID, RELATED, activity_pg(), backup_pg(), BUILDER, READONLY_TX('PostgreSQL')],
         details=[
             'Sidebar with tables, views, <strong>materialized views</strong>, functions and procedures, by schema; switch databases with <code>⌘K</code>',
             'Errors show the <code>DETAIL</code> and <code>HINT</code> PostgreSQL sends back',
             '<strong>Truncate cascade</strong> lists every table that references the one you empty, then runs <code>TRUNCATE … CASCADE</code>',
             '<strong>Health</strong> points out unused and duplicate indexes, invalid indexes, dead rows, stale statistics and XID wraparound risk, each with the command that fixes it (<code>DROP INDEX</code>, <code>VACUUM</code>…), which never runs on its own',
             '<strong>Settings</strong> lists <code>pg_settings</code> with defaults and the source of each value; <em>Review with AI</em> suggests changes as <code>ALTER SYSTEM</code> commands',
             'Cancel a running query from the editor; reset <code>pg_stat_statements</code> from the Activity tab',
             'Filters on any column (=, contains, IN, BETWEEN, IS NULL…) or a free <code>WHERE</code>',
             'Database diagram from the foreign keys, exported as PNG or SVG',
         ],
         notyet=['Restoring a backup from inside the app (use <code>pg_restore</code>)', 'A visual EXPLAIN plan'],
         faq=[('Is NavQL a free alternative to pgAdmin?',
               'Yes. NavQL is free for personal and commercial work. Unlike pgAdmin it also opens MySQL, SQL Server, '
               'MongoDB, Redis and SQLite in the same app. pgAdmin is PostgreSQL only and has more server administration '
               'screens, such as roles and restore.'),
              ('Which PostgreSQL versions does NavQL work with?',
               'NavQL talks to PostgreSQL with the standard pg driver, so current releases work. For backups the app '
               'uses the newest pg_dump it finds on your computer, which must be the same version as the server or newer.'),
              ('Does NavQL work with Supabase, Neon, TimescaleDB and CockroachDB?',
               'Yes. They speak the PostgreSQL protocol and appear in the connection form with their own name and icon. '
               'Each has its own page on this site with the details.'),
              ('Can NavQL show slow queries in PostgreSQL?',
               'Yes. The Activity tab lists top queries by total time, calls, mean, max and rows from pg_stat_statements. '
               'If the extension is not enabled, the screen explains how to turn it on.')]),
    dict(slug='mysql-client', name='MySQL', kind='core', shot='query',
         title='MySQL client for Mac, Windows and Linux — NavQL',
         desc='Free MySQL client for Mac, Windows and Linux: fast grid, SQL autocomplete, visual query builder, top queries with rows examined and mysqldump backups.',
         h1='A free MySQL client, <span class="hl">fast and careful.</span>',
         lead='Query, browse and edit MySQL in a native-feeling desktop app, see which statements read too many rows, '
              'and take a consistent backup without leaving it.',
         facts=[('MySQL', 'plus MariaDB and TiDB'), ('mysqldump backups', '--single-transaction, gzip'),
                ('Rows examined', 'per statement'), ('Free', 'macOS · Windows · Linux')],
         cards=[SQL_GRID, EDITOR,
                ('Top queries, with rows examined',
                 'From <code>performance_schema</code>: total time, calls, mean, max, rows and <strong>rows examined</strong>, '
                 'shown in orange when a statement reads hundreds of rows for each one it returns, a sign of a missing index.'),
                ('Backups with mysqldump',
                 'One click runs <code>mysqldump --single-transaction --quick</code> in the background and writes a '
                 '<code>.sql.gz</code>, through the SSH tunnel if the connection uses one.'),
                RELATED, READONLY_TX('MySQL')],
         details=[
             'Sessions with <code>KILL QUERY</code> to cancel a statement and <code>KILL</code> to end a connection',
             '<strong>Health</strong> finds unused and duplicate indexes, tables read by full scans, tables without a primary key and free space to reclaim with <code>OPTIMIZE TABLE</code>',
             '<strong>Settings</strong> from <code>variables_info</code>, with defaults; suggested changes come as <code>SET PERSIST</code>',
             'On MySQL 8, open a top query in the editor as a real execution with its values',
             '<strong>Truncate cascade</strong>: MySQL has no cascade, so NavQL empties each referencing table with foreign key checks off for that connection only',
             'DDL from <code>SHOW CREATE</code>; edit columns in place, applied as one <code>ALTER TABLE</code>',
             'Visual query builder with foreign-key joins, aggregates and <code>HAVING</code>',
             'Database diagram, export to CSV, JSON and SQL, CSV import',
         ],
         notyet=['Restoring a backup from inside the app (use the <code>mysql</code> client)', 'A visual EXPLAIN plan'],
         faq=[('Is NavQL a free alternative to MySQL Workbench?',
               'NavQL is free and covers daily work with MySQL: browsing, editing, queries, structure, monitoring and '
               'backups. It does not do data modeling or server provisioning like MySQL Workbench.'),
              ('Can I connect to MySQL over SSH?',
               'Yes. Every connection can use a built-in SSH tunnel with a password or private key, plus SSL/TLS.'),
              ('Why are top queries empty?',
               'They come from performance_schema. When statement collection is off, the Activity tab explains how to turn it on.'),
              ('Does NavQL support TiDB and MariaDB?',
               'Yes, both have their own page. MariaDB uses the same features as MySQL; TiDB adds statements_summary for top queries.')]),
    dict(slug='mariadb-client', name='MariaDB', kind='core', shot='structure',
         title='MariaDB client for Mac, Windows and Linux — NavQL',
         desc='Free MariaDB client for Mac, Windows and Linux: grid with pending changes, ALTER TABLE in place, server activity, health checks and mysqldump backups.',
         h1='A free MariaDB client <span class="hl">for everyday work.</span>',
         lead='Open MariaDB next to your other databases, edit data and structure safely, and see how the server is doing.',
         facts=[('MariaDB', 'its own entry in the form'), ('mysqldump backups', '.sql.gz in the background'),
                ('ALTER TABLE', 'edit columns in place'), ('Free', 'macOS · Windows · Linux')],
         cards=[SQL_GRID, ALTER,
                ('Activity and health',
                 'Sessions with their queries and locks, <code>KILL QUERY</code> and <code>KILL</code>, top queries with rows '
                 'examined, and a health check for unused indexes, full scans and space to reclaim with <code>OPTIMIZE TABLE</code>.'),
                ('Backups with mysqldump',
                 'One click runs <code>mysqldump --single-transaction --quick</code> in the background and gives you a '
                 'compressed <code>.sql.gz</code> to download.'),
                RELATED, BUILDER],
         details=[
             '<strong>Settings</strong> from <code>SYSTEM_VARIABLES</code>, with defaults and whether a change needs a restart',
             'Read-only connections run statements inside a <code>READ ONLY</code> transaction',
             'SQL editor with autocomplete, formatting and several result tabs',
             'Follow a foreign key from a cell to the referenced row',
             'Truncate cascade across the tables that reference the one you empty',
             'Database diagram, CSV/JSON/SQL export and CSV import',
             'SSH tunnel, SSL, Safe mode (confirms writes with a SQL preview)',
         ],
         notyet=['Restoring a backup from inside the app', 'Creating a table from a form'],
         faq=[('Is MariaDB handled differently from MySQL?',
               'NavQL knows when it is talking to MariaDB: ALTER TABLE statements and server settings use MariaDB\'s own '
               'syntax and tables. Everything else works the same as with MySQL.'),
              ('Is NavQL free for work?',
               'Yes, free for personal and commercial work, on any number of your own computers. It is not open source.'),
              ('Can I back up a large MariaDB database?',
               'Yes. The dump is written straight to a file, never held in memory, so the size of the database does not matter. '
               'mysqldump must be installed on your computer.')]),
    dict(slug='sql-server-client', name='SQL Server', kind='core', shot='diagram',
         title='SQL Server client for Mac, Windows and Linux — NavQL',
         desc='Free SQL Server client for Mac, Windows and Linux: edit tables, follow foreign keys, see sessions, top queries and the indexes the optimizer wants.',
         h1='A SQL Server client <span class="hl">that runs on a Mac.</span>',
         lead='Work with Microsoft SQL Server from macOS, Windows or Linux: tables, queries, structure, diagram and what '
              'the server is busy with.',
         facts=[('SQL Server', 'from macOS, Windows, Linux'), ('Plan cache', 'top queries'),
                ('Missing indexes', 'the optimizer asked for'), ('Free', 'macOS · Windows · Linux')],
         cards=[SQL_GRID, RELATED,
                ('Sessions and top queries',
                 'Every session with its query and what it waits on, including blocking, and <strong>end session</strong>. '
                 'Top queries come from the plan cache: total time, calls, mean, max and rows.'),
                ('Health for SQL Server',
                 'Lists the indexes the optimizer asked for, heap tables, unused and duplicate indexes and tables without a '
                 'primary key, each with the suggested <code>CREATE INDEX</code> or other command, which never runs on its own.'),
                ALTER, DIAGRAM],
         details=[
             'Quick <code>SELECT TOP 100</code> for any table from the sidebar',
             'Structure changes run in one transaction: an error leaves the table as it was',
             '<strong>Settings</strong> from <code>sys.configurations</code>, with the defaults NavQL knows; suggested changes come as <code>sp_configure</code>',
             'Without <code>VIEW SERVER STATE</code>, the Activity tab tells you what is missing',
             'Visual query builder with foreign-key joins and aggregates',
             'SQL editor with autocomplete, several result tabs, saved queries and history',
             'SSH tunnel and SSL; read-only connections accept only reading statements',
         ],
         notyet=['Backups (use your usual SQL Server tools for now)', 'Cancelling a single query from the Activity tab: on SQL Server you end the session'],
         faq=[('Can I use SQL Server on a Mac with NavQL?',
               'Yes. NavQL runs natively on macOS (Apple Silicon) and connects to SQL Server over the network, so you do not need '
               'Windows or a virtual machine to browse and query it.'),
              ('Does NavQL back up SQL Server?',
               'Not yet. Backups cover PostgreSQL, MySQL, MariaDB, MongoDB and SQLite.'),
              ('Is NavQL a replacement for SQL Server Management Studio?',
               'For browsing, editing, queries and monitoring, often yes, and it runs on macOS and Linux too. SSMS still has far more '
               'administration features, such as Agent jobs and security management.')]),
    dict(slug='mongodb-client', name='MongoDB', kind='core', shot='connections',
         title='MongoDB GUI client for Mac, Windows and Linux — NavQL',
         desc='Free MongoDB GUI for Mac, Windows and Linux: collections in a grid, shell syntax queries, current operations, the profiler and mongodump backups.',
         h1='A MongoDB GUI <span class="hl">next to your SQL.</span>',
         lead='Browse collections, query with the shell syntax you already know, see what the server is running and back '
              'it up, in the same app as your SQL databases.',
         facts=[('Shell syntax', 'find, aggregate, updateMany…'), ('mongodump backups', 'archive, gzip'),
                ('Profiler', 'grouped by query shape'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Shell syntax in the editor',
                 '<code>db.coll.find({...}, proj).sort().limit()</code>, <code>aggregate</code>, <code>insertMany</code>, '
                 '<code>updateMany</code>, <code>countDocuments</code>, with <code>ObjectId</code>, <code>ISODate</code> and '
                 '<code>NumberLong</code>.'),
                ('Documents in a grid',
                 'Collections open in the same fast grid as tables, with a JSON filter. Nested documents open as a searchable '
                 'tree in the side panel.'),
                ('Current operations',
                 'Operations per second, WiredTiger cache, memory and queued operations from <code>serverStatus</code>; '
                 'connections and running operations from <code>$currentOp</code>, with <strong>Kill operation</strong>.'),
                ('Profiler',
                 'Reads <code>system.profile</code> of the current database, grouped by query shape, with documents examined '
                 'against documents returned. If the profiler is off, the screen shows how to turn it on.'),
                ('Backups with mongodump',
                 'One click runs <code>mongodump --archive --gzip</code> in the background; restore with '
                 '<code>mongorestore</code>.'),
                ('Read only for MongoDB',
                 'On a read-only connection the shell exposes only reading methods, and <code>aggregate</code> without '
                 '<code>$out</code> or <code>$merge</code>.')],
         details=[
             'Connection by URL, including <code>mongodb+srv://</code>',
             '<strong>Settings</strong> from <code>getCmdLineOpts</code> and <code>getParameter</code>, with the defaults NavQL knows',
             'A batched read is stopped by its cursor, with <code>killCursors</code>',
             'Export a page or a whole collection to CSV or JSON',
             'SSH tunnel and TLS',
             'Optional AI assistant that writes queries from the collection structure, never from your documents',
         ],
         notyet=['Visual query builder and diagram (SQL databases only)', 'Restoring a backup from inside the app'],
         faq=[('Is NavQL a free alternative to MongoDB Compass?',
               'NavQL is free and covers browsing, querying with shell syntax, editing, monitoring and backups. Compass has '
               'schema analysis and a visual aggregation builder that NavQL does not have; NavQL also opens your SQL databases and Redis.'),
              ('Does NavQL work with MongoDB Atlas?',
               'Yes. Paste the mongodb+srv:// connection string from Atlas and NavQL fills in the connection.'),
              ('Can NavQL show slow MongoDB queries?',
               'Yes. The Profiler view groups system.profile by query shape and compares documents examined with documents returned.')]),
    dict(slug='redis-client', name='Redis', kind='core', shot='redis',
         title='Redis GUI client for Mac, Windows and Linux — NavQL',
         desc='Free Redis GUI for Mac, Windows and Linux: keys grouped by prefix with type, TTL and size, editable values, memory, clients and the slow log.',
         h1='A Redis GUI <span class="hl">that groups your keys.</span>',
         lead='See keys grouped by prefix with their type, TTL, size and value, edit them, and watch memory, clients and '
              'the slow log, next to your SQL connections.',
         facts=[('Keys by prefix', 'user:*, session:*'), ('Slow log', 'grouped by command'),
                ('Valkey, Dragonfly', 'same features'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Keys grouped by prefix',
                 'The sidebar groups keys by their first prefix (<code>user:*</code>, <code>session:*</code>). A group opens as a '
                 'grid with a row per key: key, type, TTL, size and value.'),
                ('Edit values of any type',
                 'Strings as text; hashes, lists, sets and sorted sets as JSON. Filter the grid by key pattern and by type.'),
                ('Memory, hit rate, evictions',
                 'From <code>INFO</code>: used memory and limit, keys, hit rate, evicted keys and commands per second, with a '
                 'warning when the last RDB/AOF save failed or memory passes 90% of <code>maxmemory</code>.'),
                ('Clients',
                 '<code>CLIENT LIST</code> with the last command of each client, <strong>Unblock</strong> for clients stuck on '
                 '<code>BLPOP</code> or <code>XREAD BLOCK</code>, and <strong>Kill</strong>.'),
                ('Slow log',
                 '<code>SLOWLOG</code> grouped by command, so the expensive patterns stand out, with a reset button.'),
                ('Commands, with a safety net',
                 'Run Redis commands in the editor. On a read-only connection only reading commands are accepted '
                 '(<code>GET</code>, <code>HGETALL</code>, <code>SCAN</code>, <code>ZRANGE</code>…).')],
         details=[
             '<strong>Settings</strong> from <code>CONFIG GET *</code>, with defaults NavQL knows; suggested changes come as <code>CONFIG SET</code>',
             'Quick <code>SCAN 0 MATCH … COUNT 100</code> for any group from the sidebar',
             'SSH tunnel and TLS',
             'Works with Valkey and Dragonfly, which appear in the form with their own name and icon',
             'Connection colors and tags keep the production cache apart from local',
         ],
         notyet=['Backups (Redis has its own RDB and AOF persistence)', 'Pub/Sub and stream consumer views'],
         faq=[('Is NavQL a free alternative to RedisInsight?',
               'NavQL is free and covers keys, values, memory, clients and the slow log. RedisInsight has more Redis-specific '
               'tools, such as module support; NavQL puts Redis in the same app as your SQL databases and MongoDB.'),
              ('Does NavQL work with Valkey and Dragonfly?',
               'Yes. Both use the Redis protocol. Dragonfly has no CLIENT UNBLOCK, so that button is not offered there.'),
              ('Does NavQL use KEYS on my server?',
               'Groups are read with SCAN in batches, so browsing does not block the server the way KEYS * can.')]),
    dict(slug='sqlite-client', name='SQLite', kind='core', shot='structure',
         title='SQLite browser and editor for Mac, Windows and Linux — NavQL',
         desc='Free SQLite browser and editor for Mac, Windows and Linux: open any .sqlite file, edit rows, change columns, draw the diagram and back it up.',
         h1='Open a SQLite file. <span class="hl">See everything.</span>',
         lead='Open any .sqlite or .db file, browse and edit its tables, change its structure and draw its diagram, with '
              'the same tools you use on server databases.',
         facts=[('Any SQLite file', '.sqlite, .db'), ('Online backup', 'SQLite\'s own API'),
                ('Diagram', 'from the foreign keys'), ('Free', 'macOS · Windows · Linux')],
         cards=[SQL_GRID, ALTER, DIAGRAM, RELATED, BUILDER,
                ('Online backup',
                 'Back up a SQLite database with SQLite\'s own online backup, safe while the file is in use. The result is a '
                 'plain <code>.sqlite</code> file.')],
         details=[
             'DDL read from <code>sqlite_master</code>',
             'Read-only connections use SQLite\'s own <code>readonly</code> check on every statement',
             '<strong>Truncate cascade</strong> runs a <code>DELETE</code> on each referencing table, in one transaction',
             'SQL editor with autocomplete, formatting and several result tabs',
             'Export to CSV, JSON or SQL, and import a CSV as pending rows',
         ],
         notyet=['The Activity tab (SQLite has no server to watch)', 'Creating a new database file from the app'],
         faq=[('Is NavQL a free alternative to DB Browser for SQLite?',
               'Yes, NavQL is free. It adds a diagram, related rows, a visual query builder and the same app for your server databases.'),
              ('Can I open a SQLite file from an iOS or Android app?',
               'Yes, if you copy the file to your computer. NavQL opens any SQLite 3 database file.'),
              ('Does editing lock my SQLite file?',
               'Changes are written only when you commit, in one transaction, so the file is locked just for that moment.')]),
    # Compatible servers
    dict(slug='supabase-client', name='Supabase', kind='compat', proto='PostgreSQL', shot='query',
         title='Supabase database client for Mac, Windows and Linux — NavQL',
         desc='Open your Supabase Postgres in a free desktop client: paste the connection string, edit tables, see top queries and back up with pg_dump.',
         h1='Your Supabase database, <span class="hl">in a desktop client.</span>',
         lead='Supabase gives you a real PostgreSQL database. NavQL opens it with the tools you would want on any Postgres: '
              'grid editing, related rows, query builder, activity and backups.',
         facts=[('*.supabase.co', 'recognized from the URL'), ('pg_stat_statements', 'found in "extensions"'),
                ('pg_dump backups', 'custom format'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Paste the connection string',
                 'Import the URL from your project\'s settings and NavQL recognizes the <code>*.supabase.co</code> host, shows '
                 'Supabase with its own name and icon, and fills in the form.'),
                ('Top queries on Supabase',
                 'Supabase installs <code>pg_stat_statements</code> in the <code>extensions</code> schema; NavQL finds it there '
                 'and lists top queries by total time, calls, mean and rows.'),
                SQL_GRID, RELATED, backup_pg(), READONLY_TX('Supabase\'s PostgreSQL')],
         details=[
             'Every PostgreSQL feature of NavQL: structure editing, diagram, visual query builder, health checks',
             'Sessions with cancel and terminate, and who blocks whom',
             'SQL editor with autocomplete for your tables and columns',
             'SSL/TLS and SSH tunnel',
             'Colors and tags keep the production project apart from staging and local',
         ],
         notyet=['Supabase-specific screens such as Auth, Storage or Edge Functions: NavQL works with the database'],
         faq=[('How do I connect NavQL to Supabase?',
               'Copy the connection string of your project\'s database (direct or pooler) and paste it into NavQL\'s "Import from URL". '
               'NavQL recognizes Supabase from the host.'),
              ('Is it safe to browse my production Supabase database?',
               'Mark the connection Read only: NavQL then accepts only reading statements and runs them in a READ ONLY transaction.'),
              ('Can I back up a Supabase database?',
               'Yes. NavQL runs pg_dump against it; you need a pg_dump at least as new as the Postgres version of your project.')]),
    dict(slug='neon-client', name='Neon', kind='compat', proto='PostgreSQL', shot='table',
         title='Neon Postgres client for Mac, Windows and Linux — NavQL',
         desc='Open Neon serverless Postgres in a free desktop client: paste the connection string, edit tables, follow foreign keys, see top queries, back up.',
         h1='Neon Postgres, <span class="hl">browsed like a local database.</span>',
         lead='Paste your Neon connection string and work with every branch the way you work with any PostgreSQL: '
              'grid, queries, structure, activity and backups.',
         facts=[('*.neon.tech', 'recognized from the URL'), ('PostgreSQL', 'every NavQL feature'),
                ('pg_dump backups', 'in the background'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Paste the connection string',
                 'NavQL recognizes the <code>*.neon.tech</code> host when you import the URL, and shows Neon with its own name and icon.'),
                ('One connection per branch',
                 'Save each Neon branch as its own connection, with a color and tag, and group them in a project so '
                 'production never looks like a preview branch.'),
                SQL_GRID, RELATED, activity_pg('Neon'), backup_pg()],
         details=[
             'Structure editing with <code>ALTER TABLE</code>, diagram and visual query builder',
             'Read-only connections with a <code>READ ONLY</code> transaction',
             'SQL editor with autocomplete, saved queries and history',
             'Export to CSV, JSON or SQL; import CSV as pending rows',
             'SSL for hosted databases',
         ],
         notyet=['Neon-specific screens such as creating branches: use the Neon console for that'],
         faq=[('How do I connect NavQL to Neon?',
               'Copy the connection string from the Neon console and paste it into "Import from URL" in NavQL.'),
              ('Can I back up a Neon branch?',
               'Yes, with pg_dump from NavQL. Use a pg_dump at least as new as the branch\'s Postgres version.')]),
    dict(slug='cockroachdb-client', name='CockroachDB', kind='compat', proto='PostgreSQL', shot='diagram-focus',
         title='CockroachDB client for Mac, Windows and Linux — NavQL',
         desc='Free CockroachDB client for Mac, Windows and Linux: detects the cluster version, cancels with CANCEL QUERIES and lists cluster settings.',
         h1='A CockroachDB client <span class="hl">that knows it is not Postgres.</span>',
         lead='CockroachDB speaks the PostgreSQL protocol, but not everything works the same. NavQL handles the differences '
              'so the grid, editor, activity and settings just work.',
         facts=[('CockroachDB 26.4', 'shown in the status bar'), ('CANCEL QUERIES', 'instead of pg_cancel_backend'),
                ('Cluster settings', 'SHOW CLUSTER SETTINGS'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Detected, not assumed',
                 'The status bar shows the real server, such as <code>CockroachDB 26.4.0</code>. URLs with '
                 '<code>cockroachdb://</code> or a <code>*.cockroachlabs.cloud</code> host are recognized on import.'),
                ('Cancel the CockroachDB way',
                 'There is no <code>pg_cancel_backend</code> on CockroachDB, so NavQL cancels with <code>CANCEL QUERIES</code>, '
                 'from the editor and from the Activity tab.'),
                ('Cluster settings',
                 'The Settings view reads <code>SHOW CLUSTER SETTINGS</code>, separating changed and important ones from all.'),
                ('Clean autocomplete',
                 'Internal schemas such as <code>crdb_internal</code> stay out of autocomplete, so suggestions are your tables.'),
                SQL_GRID, RELATED],
         details=[
             'Structure, DDL and database diagram from the foreign keys',
             'Visual query builder with foreign-key joins and aggregates',
             'Read-only connections accept only reading statements',
             'SSH tunnel and SSL, with colors and tags per connection',
             'Export to CSV, JSON or SQL',
         ],
         notyet=['Backups (pg_dump does not support CockroachDB; use CockroachDB\'s BACKUP)'],
         faq=[('Does NavQL support CockroachDB Cloud?',
               'Yes. Paste the connection string; NavQL recognizes *.cockroachlabs.cloud and uses SSL.'),
              ('Why does NavQL not back up CockroachDB?',
               'Its backups use pg_dump, which CockroachDB does not support. CockroachDB has its own BACKUP statement.'),
              ('Which PostgreSQL features work on CockroachDB?',
               'The grid, editor, structure, diagram, related rows, query builder, sessions and settings all work. Where CockroachDB '
               'differs, such as cancelling queries, NavQL uses its own commands.')]),
    dict(slug='timescaledb-client', name='TimescaleDB', kind='compat', proto='PostgreSQL', shot='query',
         title='TimescaleDB client for Mac, Windows and Linux — NavQL',
         desc='Free TimescaleDB client for Mac, Windows and Linux: shows the TimescaleDB version, clean autocomplete and every PostgreSQL tool, pg_dump included.',
         h1='TimescaleDB with <span class="hl">every Postgres tool.</span>',
         lead='TimescaleDB is PostgreSQL with time-series superpowers. NavQL recognizes the extension and gives you the full '
              'PostgreSQL toolset on top.',
         facts=[('PostgreSQL 16 · TimescaleDB 2.31', 'in the status bar'), ('Clean autocomplete', 'no _timescaledb_*'),
                ('pg_dump backups', 'custom format'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Detected in the status bar',
                 'NavQL shows both versions, such as <code>PostgreSQL 16 · TimescaleDB 2.31</code>, so you know what you are '
                 'connected to.'),
                ('Clean autocomplete',
                 'Internal schemas (<code>_timescaledb_*</code>) stay out of autocomplete; your hypertables and views are what you see.'),
                EDITOR, activity_pg('TimescaleDB'), backup_pg(), BUILDER],
         details=[
             'Grid editing with pending changes and a transactional commit',
             'Related rows and foreign-key navigation',
             'Health checks and Settings from <code>pg_settings</code>',
             'Read-only connections with a <code>READ ONLY</code> transaction',
             'Export to CSV, JSON or SQL',
         ],
         notyet=['TimescaleDB-specific screens such as hypertable chunks or compression policies: query them in the editor'],
         faq=[('Does NavQL work with Timescale Cloud?',
               'Yes. It is PostgreSQL with the TimescaleDB extension; paste the connection string and NavQL connects with SSL.'),
              ('Can I back up a TimescaleDB database?',
               'Yes, with pg_dump. Follow Timescale\'s own guidance for restoring, which needs the extension installed first.')]),
    dict(slug='tidb-client', name='TiDB', kind='compat', proto='MySQL', shot='structure',
         title='TiDB client for Mac, Windows and Linux — NavQL',
         desc='Free TiDB client for Mac, Windows and Linux: top queries from statements_summary with rows examined, safe read-only mode and TiDB settings.',
         h1='A TiDB client <span class="hl">with real top queries.</span>',
         lead='TiDB speaks the MySQL protocol. NavQL uses TiDB\'s own statement statistics and settings, and keeps read-only '
              'connections safe even though TiDB has no READ ONLY transaction.',
         facts=[('statements_summary', 'top queries'), ('Rows examined', 'per statement'),
                ('Read only', 'always rolled back'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Top queries from statements_summary',
                 'Total time, calls, mean, max, rows and <strong>rows examined</strong>, with a warning when a statement reads '
                 'far more rows than it returns. Open one in the editor as a real execution with its values.'),
                ('Read only without READ ONLY',
                 'TiDB has no <code>READ ONLY</code> transaction, so on a read-only connection NavQL runs each statement in a '
                 'transaction that is always rolled back.'),
                ('Detected, with its settings',
                 'The status bar shows the real server (<code>TiDB 7.5.1</code>); <code>tidb://</code> and '
                 '<code>*.tidbcloud.com</code> URLs are recognized; Settings reads <code>VARIABLES_INFO</code>.'),
                SQL_GRID, RELATED, BUILDER],
         details=[
             'Sessions with <code>KILL QUERY</code> and <code>KILL</code>',
             'Structure, DDL and diagram from the foreign keys',
             'SQL editor with autocomplete and several result tabs',
             'Export to CSV, JSON or SQL; import CSV',
             'SSH tunnel and SSL',
         ],
         notyet=['Backups (use TiDB\'s BR or Dumpling)'],
         faq=[('Does NavQL work with TiDB Cloud Serverless?',
               'Yes. Paste the connection string; NavQL recognizes *.tidbcloud.com and connects with SSL.'),
              ('Why are TiDB backups not available?',
               'NavQL\'s backups use mysqldump, which is not the recommended tool for TiDB. Use BR or Dumpling.')]),
    dict(slug='valkey-client', name='Valkey', kind='compat', proto='Redis', shot='redis',
         title='Valkey GUI client for Mac, Windows and Linux — NavQL',
         desc='Free Valkey GUI for Mac, Windows and Linux: keys grouped by prefix, editable values, memory and hit rate, clients and the slow log.',
         h1='A Valkey GUI, <span class="hl">ready on day one.</span>',
         lead='Valkey keeps the Redis protocol, so NavQL gives it every Redis feature: keys by prefix, values, memory, '
              'clients and the slow log.',
         facts=[('valkey://', 'recognized on import'), ('Keys by prefix', 'type, TTL, size'),
                ('Slow log', 'grouped by command'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Its own entry',
                 'Valkey appears in the connection form with its own name and icon, and <code>valkey://</code> URLs are recognized.'),
                ('Keys grouped by prefix',
                 'Groups such as <code>user:*</code> open as a grid with key, type, TTL, size and value; edit values of any type.'),
                ('Memory and hit rate',
                 'Used memory and limit, keys, hit rate, evictions and commands per second, with warnings for failed saves and '
                 'memory near <code>maxmemory</code>.'),
                ('Clients',
                 '<code>CLIENT LIST</code> with the last command of each client, <strong>Unblock</strong> and <strong>Kill</strong>.'),
                ('Slow log', '<code>SLOWLOG</code> grouped by command, with reset.'),
                ('Read only', 'Read-only connections accept only reading commands.')],
         details=[
             'Settings from <code>CONFIG GET *</code>; suggested changes as <code>CONFIG SET</code>',
             'SSH tunnel and TLS',
             'Same app as your PostgreSQL, MySQL and MongoDB connections',
         ],
         notyet=['Backups (Valkey has its own RDB and AOF persistence)'],
         faq=[('Is Valkey handled differently from Redis?',
               'NavQL uses the same features for both and shows Valkey by name, so you always know which server you are on.')]),
    dict(slug='dragonfly-client', name='Dragonfly', kind='compat', proto='Redis', shot='redis',
         title='Dragonfly GUI client for Mac, Windows and Linux — NavQL',
         desc='Free Dragonfly GUI for Mac, Windows and Linux: keys grouped by prefix, editable values, memory and hit rate, clients and the slow log.',
         h1='A Dragonfly GUI <span class="hl">for your keys.</span>',
         lead='Dragonfly speaks the Redis protocol. NavQL opens it with keys by prefix, value editing, memory, clients and '
              'the slow log, and skips what Dragonfly does not support.',
         facts=[('Dragonfly', 'its own entry in the form'), ('Keys by prefix', 'type, TTL, size'),
                ('Slow log', 'grouped by command'), ('Free', 'macOS · Windows · Linux')],
         cards=[('Its own entry',
                 'Dragonfly appears in the connection form with its own name and icon, and the status bar shows the real server.'),
                ('Keys grouped by prefix',
                 'Groups such as <code>session:*</code> open as a grid with key, type, TTL, size and value; edit values of any type.'),
                ('Memory and hit rate',
                 'Used memory and limit, keys, hit rate, evictions and commands per second from <code>INFO</code>.'),
                ('Clients',
                 '<code>CLIENT LIST</code> with <strong>Kill</strong>. Dragonfly has no <code>CLIENT UNBLOCK</code>, so NavQL does not offer it.'),
                ('Slow log', '<code>SLOWLOG</code> grouped by command, with reset.'),
                ('Read only', 'Read-only connections accept only reading commands.')],
         details=[
             'Settings from <code>CONFIG GET *</code>',
             'SSH tunnel and TLS',
             'Same app as your SQL databases and MongoDB',
         ],
         notyet=['Backups (use Dragonfly\'s own snapshots)'],
         faq=[('Does every Redis feature of NavQL work on Dragonfly?',
               'All but Unblock, because Dragonfly does not implement CLIENT UNBLOCK.')]),
]

# ---------------------------------------------------------------------------------------------
# Comparison pages
#
# Only facts about the other product that its own website states (read on CHECKED), or that are
# plain and long-standing (e.g. pgAdmin is for PostgreSQL). "Not listed" means we looked at their
# site and did not find it, which is what we can honestly say.

ALTS = [
    dict(slug='tableplus', name='TablePlus', site='https://tableplus.com/', shot='table',
         desc='NavQL vs TablePlus, honestly: where TablePlus is the better pick, and what NavQL adds for free: related rows, query builder and server activity.',
         lead='TablePlus is a polished, native database client. NavQL was inspired by it and follows a similar workflow, '
              'but it is free without limits and adds tools for following data and watching the server.',
         rows=[('Price model', 'Free for personal and commercial work', 'Paid license; the free trial is limited to 2 open tabs, 2 windows and 2 advanced filters at a time (per its pricing page)'),
               ('Platforms', 'macOS (Apple Silicon), Windows, Linux', 'macOS, Windows, Linux, iPhone and iPad'),
               ('Related rows as a tree', 'Yes, following foreign keys in both directions', 'Not listed on its website'),
               ('Visual query builder', 'Yes', 'Not listed on its website'),
               ('Server activity, top queries, health', 'Yes, in an Activity tab', 'Not listed on its website'),
               ('Backups', 'pg_dump, mysqldump, mongodump, SQLite online backup; restore with the database\'s own tool', 'Scheduled backup and restore (per its website)'),
               ('Databases', 'PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis and compatible servers', 'A longer list, including Oracle, ClickHouse, DuckDB, Cassandra, Snowflake and CockroachDB')],
         them=['You want an app for iPhone and iPad as well', 'You need a database NavQL does not support yet, such as Oracle or ClickHouse', 'You want scheduled backups and restore from the app', 'You prefer a fully native app on each platform'],
         us=['You want every feature without a license or trial limits', 'You often follow data across foreign keys and want the whole tree of related rows', 'You want to see sessions, top queries and health checks without another tool'],
         faq=[('Is NavQL a TablePlus clone?',
               'NavQL was inspired by TablePlus and follows a similar workflow (connections, grid, pending changes, ⌘S to commit), '
               'but it is its own app with its own features, such as related rows, the query builder and the Activity tab.'),
              ('Is NavQL free like the TablePlus trial?',
               'NavQL is free without tab, window or filter limits, for personal and commercial work.')]),
    dict(slug='dbeaver', name='DBeaver', site='https://dbeaver.io/', shot='diagram-focus',
         desc='NavQL vs DBeaver, honestly: DBeaver supports more databases; NavQL is a focused free client with related rows, top queries and MongoDB and Redis.',
         lead='DBeaver is a powerful universal tool with support for a very long list of databases. NavQL is narrower and '
              'more focused: fewer databases, fewer menus, and tools for the questions you ask every day.',
         rows=[('Price model', 'Free for personal and commercial work (not open source)', 'Community Edition is free and open source; paid editions are offered too'),
               ('Runtime', 'Electron desktop app', 'Requires Java; downloads bundle OpenJDK (per its download page)'),
               ('Databases', 'PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis and compatible servers', 'Many more SQL databases; MongoDB and Redis are listed under DBeaver PRO, not the Community Edition (per dbeaver.io)'),
               ('Related rows as a tree', 'Yes, following foreign keys in both directions', 'Not listed on its website'),
               ('Top queries and health checks', 'Yes, from the server\'s own statistics, with suggested fixes', 'Not listed on its website'),
               ('Visual query builder', 'Yes', 'Listed under DBeaver PRO on dbeaver.io'),
               ('ER diagram', 'Yes', 'Yes')],
         them=['You need a database NavQL does not support, such as Oracle, ClickHouse or DuckDB', 'You want an open-source tool', 'You need data transfer, comparison or other advanced tasks'],
         us=['You want a fast, focused app with less to configure', 'You want MongoDB and Redis next to SQL in a free app', 'You want top queries, health checks and server settings in one view'],
         faq=[('Does NavQL support as many databases as DBeaver?',
               'No. NavQL supports PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB and Redis, plus compatible servers. '
               'DBeaver supports many more.'),
              ('Is NavQL open source like DBeaver Community?',
               'No. NavQL is free of charge but not open source.')]),
    dict(slug='datagrip', name='DataGrip', site='https://www.jetbrains.com/datagrip/', shot='query',
         desc='NavQL vs DataGrip, honestly: DataGrip is a deep SQL IDE; NavQL is a lighter client, free for work, with related rows, server activity and backups.',
         lead='DataGrip is a full SQL IDE from JetBrains, with deep code analysis and refactoring. NavQL is a lighter client '
              'focused on browsing data, following relationships and keeping an eye on the server.',
         rows=[('Price model', 'Free for personal and commercial work', 'Free for non-commercial use; commercial use requires a subscription (per its website)'),
               ('Focus', 'Browsing, editing and following data, plus server health', 'Writing and refactoring SQL, as an IDE'),
               ('Related rows as a tree', 'Yes, following foreign keys in both directions', 'Navigation between related tables; a tree of related rows is not listed'),
               ('Visual query builder', 'Yes', 'Not listed on its website'),
               ('Sessions, top queries and health', 'Yes, in an Activity tab', 'Not listed on its website'),
               ('One-click backups', 'pg_dump, mysqldump, mongodump, SQLite', 'Not listed (it lists data export and import)'),
               ('Databases', 'PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis and compatible servers', 'A longer list, see its website')],
         them=['You write a lot of SQL and want IDE-level analysis and refactoring', 'You already use other JetBrains IDEs', 'You need a database NavQL does not support'],
         us=['You want a client that is free for commercial work too', 'You spend more time reading and following data than writing long SQL', 'You want to see what the server is doing and back it up from the same app'],
         faq=[('Is NavQL an IDE like DataGrip?',
               'No. NavQL has a capable SQL editor with autocomplete, but it is a database client, not an IDE.')]),
    dict(slug='beekeeper-studio', name='Beekeeper Studio', site='https://www.beekeeperstudio.io/', shot='connections',
         desc='NavQL vs Beekeeper Studio, honestly: Beekeeper is open source with more databases; NavQL adds related rows and server activity, all free.',
         lead='Beekeeper Studio is a friendly, modern SQL editor and database manager with an open-source community edition. '
              'NavQL is close in spirit, and goes further into following data and watching the server.',
         rows=[('Price model', 'Free for personal and commercial work (not open source)', 'Open-source Community edition plus paid editions (per its website)'),
               ('Databases', 'PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis and compatible servers', '26 listed on its website, including Oracle, ClickHouse, DuckDB, Cassandra and Snowflake'),
               ('TimescaleDB, Valkey, Dragonfly by name', 'Yes', 'Not listed on its website'),
               ('Related rows as a tree', 'Yes', 'Not listed on its website'),
               ('Sessions, top queries and health', 'Yes, in an Activity tab', 'Not listed on its website'),
               ('Backups', 'pg_dump, mysqldump, mongodump, SQLite online backup', 'Backup and restore in the paid editions (per its pricing page)'),
               ('Free edition limits', 'None', 'Community edition: at most 2 filters per table; JSON sidebar, MongoDB and editing query results are paid (per its pricing page)')],
         them=['You want an open-source tool', 'You need Oracle, ClickHouse, DuckDB, Snowflake or another database NavQL does not support', 'You want cloud workspaces to share connections with a team'],
         us=['You want every feature free, without a paid tier', 'You want the tree of related rows and the server Activity tab', 'You use Redis, Valkey or Dragonfly next to SQL'],
         faq=[('Is NavQL open source like Beekeeper Studio\'s community edition?',
               'No. NavQL is free of charge but not open source.')]),
    dict(slug='pgadmin', name='pgAdmin', site='https://www.pgadmin.org/', shot='table',
         desc='NavQL vs pgAdmin, honestly: pgAdmin is the PostgreSQL admin tool; NavQL is a free multi-database client with related rows and top queries.',
         lead='pgAdmin is the long-standing open-source administration tool for PostgreSQL. NavQL covers day-to-day work on '
              'PostgreSQL with a faster grid and more ways to follow data, and opens your other databases too.',
         rows=[('Price model', 'Free (not open source)', 'Free and open source'),
               ('Databases', 'PostgreSQL and compatible servers, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis', 'PostgreSQL'),
               ('Form', 'Desktop app', 'Desktop or server (web) mode'),
               ('Activity monitoring', 'Sessions, cancel and terminate, top queries, health', 'Monitoring dashboard and activity monitoring (per its website)'),
               ('Related rows as a tree', 'Yes, following foreign keys in both directions', 'Not listed on its website'),
               ('Top queries from pg_stat_statements', 'Yes, in the Activity tab', 'Not listed on its website'),
               ('Health checks with suggested fixes', 'Yes (unused indexes, dead rows, wraparound…)', 'Not listed on its website'),
               ('Backup and restore', 'Backup with pg_dump; restore with pg_restore yourself', 'Backup, restore, vacuum and analyze from the interface')],
         them=['You administer PostgreSQL servers: roles, restore and server objects', 'You want a web interface that a team reaches in the browser', 'You want an open-source tool'],
         us=['You also use MySQL, SQL Server, MongoDB or Redis and want one app', 'You want pending changes with a SQL preview and one transactional commit', 'You want top queries and health checks without writing the SQL yourself'],
         faq=[('Can NavQL replace pgAdmin?',
               'For browsing, editing, queries, monitoring and backups, often yes. For administering roles, restoring and other '
               'server objects, pgAdmin does more.')]),
    dict(slug='navicat', name='Navicat', site='https://www.navicat.com/', shot='diagram',
         desc='NavQL vs Navicat, honestly: Navicat is a commercial suite; NavQL is a free client with related rows, server monitoring built in and backups.',
         lead='Navicat is a commercial suite with data modeling, synchronization and many database products. NavQL is a free '
              'client that covers the daily work, with server monitoring built in.',
         rows=[('Price model', 'Free for personal and commercial work, every feature', 'Commercial with a free trial; Navicat Premium Lite is a free version with basic features (per its website)'),
               ('Platforms', 'macOS (Apple Silicon), Windows, Linux', 'Windows, macOS, Linux'),
               ('Related rows as a tree', 'Yes, following foreign keys in both directions', 'Not listed on its website'),
               ('Server monitoring', 'Built in: sessions, top queries, health, settings', 'Navicat Monitor, a separate product'),
               ('Data modeling', 'Diagram of an existing database', 'Navicat Data Modeler, a separate product'),
               ('Databases', 'PostgreSQL, MySQL, MariaDB, SQL Server, SQLite, MongoDB, Redis and compatible servers by name', 'Navicat Premium: MySQL, PostgreSQL, SQL Server, Oracle, SQLite, MariaDB, MongoDB, Redis and Snowflake')],
         them=['You need data migration and synchronization between servers', 'You need Oracle or Snowflake', 'Your company already licenses Navicat'],
         us=['You want a free client for commercial work', 'You want monitoring in the same app as your data', 'You want to follow rows across foreign keys as a tree'],
         faq=[('Does NavQL do data modeling like Navicat?',
               'No. NavQL draws the diagram of an existing database and edits columns in place, but it is not a modeling tool.')]),
    dict(slug='db-pro', name='DB Pro', site='https://dbpro.app/', shot='connections',
         desc='NavQL vs DB Pro, honestly: DB Pro has ClickHouse, DynamoDB and dashboards; NavQL is free without limits, with server activity and backups.',
         lead='DB Pro is a modern desktop database client with dashboards and an AI chat. NavQL is free without connection or '
              'tab limits and focuses on following data, watching the server and backing it up.',
         rows=[('Price model', 'Free for personal and commercial work, no limits', 'Free plan limited to 2 connections, 3 open tabs, 5 saved queries and 1 device; paid plans remove limits (per its pricing page)'),
               ('Platforms', 'macOS (Apple Silicon), Windows, Linux', 'macOS, Windows, Linux'),
               ('Active sessions and cancelling queries', 'Yes, with top queries and health checks', 'On its public roadmap, not yet available'),
               ('Backups', 'pg_dump, mysqldump, mongodump, SQLite online backup', 'Not listed on its website'),
               ('Visual query builder', 'Yes', 'Not listed on its website'),
               ('Read-only connections', 'Yes, with READ ONLY transactions on PostgreSQL and MySQL', 'Not listed on its website (it lists guard rails for its AI chat)'),
               ('Related rows as a tree', 'Yes', 'Not listed on its website'),
               ('CockroachDB, TimescaleDB, TiDB, Valkey, Dragonfly', 'Yes, detected by name', 'Not listed on its website'),
               ('ClickHouse, DynamoDB, Turso, PlanetScale', 'No', 'Yes'),
               ('AI providers', 'Anthropic (your own key)', 'OpenAI, Anthropic, Google, Ollama, OpenRouter')],
         them=['You use ClickHouse, DynamoDB or Turso', 'You want dashboards built from queries', 'You want to choose between several AI providers or a local model'],
         us=['You want more than 2 connections and 3 tabs without paying', 'You want to see sessions, cancel queries and find slow statements today', 'You want one-click backups and real read-only connections'],
         faq=[('Is DB Pro free?',
               'It has a free plan with limits (2 connections, 3 open tabs, 5 saved queries, 1 device) and paid plans. NavQL is free without those limits.')]),
]

# ---------------------------------------------------------------------------------------------
# HTML

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
         '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">')


def text(s):
    """HTML fragment → plain text for meta tags and JSON-LD."""
    return html.unescape(re.sub(r'<[^>]+>', '', s))


def esc(s):
    return html.escape(s, quote=True)


def ld(data):
    return '<script type="application/ld+json">' + json.dumps(data, ensure_ascii=False).replace('</', '<\\/') + '</script>'


def head(title, desc, path, image_alt, data):
    url = SITE + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="NavQL">
<meta property="og:locale" content="en_US">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(image_alt)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og.png">
{ld(data)}
<meta name="theme-color" content="#0A0A0B">
<meta name="color-scheme" content="dark">
{FONTS}
<link rel="stylesheet" href="/assets/pages.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>

<header class="site-header">
  <div class="wrap">
    <a class="brand" href="/" aria-label="NavQL home"><img src="/assets/navql-logo-fundo-escuro.svg" alt="NavQL" width="92" height="28"></a>
    <nav aria-label="Main">
      <a href="/#databases" class="hide-sm">Databases</a>
      <a href="/alternatives/"{' aria-current="page"' if path.startswith('/alternatives/') else ''}>Compare</a>
      <a href="/#download" class="btn btn-primary btn-sm">Download</a>
    </nav>
  </div>
</header>
'''


def footer_html():
    core = [d for d in DATABASES if d['kind'] == 'core']
    compat = [d for d in DATABASES if d['kind'] == 'compat']
    li = lambda href, label: f'<li><a href="{href}">{label}</a></li>'
    col = lambda title, items: f'<div><h2>{title}</h2><ul>{"".join(items)}</ul></div>'
    return f'''<footer class="site-footer">
  <div class="wrap">
    <div class="footer-top">
      <div>
        <a class="brand" href="/" aria-label="NavQL home"><img src="/assets/navql-logo-fundo-escuro.svg" alt="NavQL" width="79" height="24"></a>
        <p>Free database client for macOS, Windows and Linux.</p>
      </div>
      {col('Databases', [li(f'/{d["slug"]}/', d['name']) for d in core])}
      {col('Compatible servers', [li(f'/{d["slug"]}/', d['name']) for d in compat])}
      {col('Compare', [li(f'/alternatives/{a["slug"]}/', f'vs {a["name"]}') for a in ALTS] + [li('/alternatives/', 'All comparisons')])}
      {col('NavQL', [li('/#download', 'Download'), li('/#faq', 'FAQ'), li('https://github.com/navql/releases/releases', 'Releases'), li('/privacy.html', 'Privacy'), li('/terms.html', 'Terms'), li('/llms.txt', 'llms.txt')])}
    </div>
    <p class="footer-bottom">© 2026 NavQL</p>
  </div>
</footer>
'''


def tail():
    return footer_html() + '</body>\n</html>\n'


def caption(name, db=None):
    shown = SHOT_DB.get(name, 'PostgreSQL')
    if shown is None:
        return 'A real NavQL screen: the connections of one project.'
    if db and db not in (shown, 'Supabase', 'Neon', 'TimescaleDB') or (db is None and shown != 'PostgreSQL'):
        return f'A real NavQL screen, shown on {shown}.' + (f' The same screens work on {db}.' if db else '')
    if db in ('Valkey', 'Dragonfly'):
        return f'A real NavQL screen, shown on Redis. The same screens work on {db}.'
    return f'A real NavQL screen, shown on {shown}.'


def shot(name, eager=True):
    return (f'<div class="shot"><img src="/assets/shots/{name}-1440.webp" '
            f'srcset="/assets/shots/{name}-1440.webp 1440w, /assets/shots/{name}.webp 2880w" '
            f'sizes="(max-width: 1080px) 100vw, 660px" alt="{esc(SHOTS[name])}" width="2880" height="1800"'
            + (' fetchpriority="high"' if eager else ' loading="lazy"') + '></div>')


def crumbs(items):
    lis = ''.join(f'<li><a href="{h}">{esc(n)}</a></li>' if h else f'<li aria-current="page">{esc(n)}</li>' for n, h in items)
    return f'<ol class="crumbs" aria-label="Breadcrumb">{lis}</ol>'


def crumbs_ld(items):
    return {'@context': 'https://schema.org', '@type': 'BreadcrumbList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': SITE + (h or p)}
        for i, (n, h, p) in enumerate(items)]}


def faq_ld(faq):
    return {'@context': 'https://schema.org', '@type': 'FAQPage', 'mainEntity': [
        {'@type': 'Question', 'name': q, 'acceptedAnswer': {'@type': 'Answer', 'text': a}} for q, a in faq]}


def faq_block(faq, title='Good to know.'):
    items = ''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
    return f'''  <section class="block" id="faq" aria-labelledby="faq-title">
    <div class="wrap faq-wrap">
      <div class="section-head"><p class="label">Questions</p><h2 id="faq-title">{title}</h2></div>
      <div class="faq">{items}</div>
    </div>
  </section>
'''


def cta(name=None):
    what = f'Open your {name} databases' if name else 'Try it on your own databases'
    return f'''  <section class="block cta" aria-labelledby="cta-title">
    <div class="wrap">
      <img class="icon" src="/assets/navql-icone.svg" alt="" width="64" height="64">
      <h2 id="cta-title">{what} in NavQL.</h2>
      <p class="sub">Free for macOS (Apple Silicon), Windows and Linux. Installers and terminal commands are on the download page.</p>
      <div class="actions"><a class="btn btn-primary" href="/#download">Download NavQL</a><a class="btn btn-secondary" href="/#demo">Watch the demo</a></div>
    </div>
  </section>
'''


def db_links(current):
    items = []
    for d in DATABASES:
        if d['slug'] == current:
            continue
        sub = f'{d["proto"]} protocol' if d['kind'] == 'compat' else 'Database'
        items.append(f'<li><a href="/{d["slug"]}/"><strong>{d["name"]}</strong><span>{sub}</span></a></li>')
    return f'''  <section class="block" aria-labelledby="more-title">
    <div class="wrap">
      <div class="section-head"><p class="label">One app</p><h2 id="more-title">Every database you use, side by side.</h2>
      <p>NavQL keeps all your connections in one place, each with its own color and tag. <a class="inline" href="/alternatives/">See how NavQL compares</a> with other clients.</p></div>
      <ul class="links">{''.join(items)}</ul>
    </div>
  </section>
'''


def app_ld(desc, features, path):
    return {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': 'NavQL', 'url': SITE + '/',
            'description': desc, 'applicationCategory': 'DeveloperApplication', 'applicationSubCategory': 'Database client',
            'operatingSystem': 'macOS, Windows, Linux', 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'},
            'downloadUrl': SITE + '/#download', 'image': SITE + '/assets/og.png', 'featureList': features,
            'mainEntityOfPage': SITE + path}


def db_page(d):
    path = f'/{d["slug"]}/'
    trail = [('NavQL', '/', '/'), (f'{d["name"]} client', None, path)]
    features = [text(t) for t, _ in d['cards']]
    data = [app_ld(d['desc'], features, path),
            {'@context': 'https://schema.org', '@type': 'WebPage', 'name': d['title'], 'url': SITE + path,
             'description': d['desc'], 'inLanguage': 'en', 'dateModified': LASTMOD,
             'about': {'@type': 'SoftwareApplication', 'name': d['name']}},
            crumbs_ld(trail), faq_ld(d['faq'])]
    out = head(d['title'], d['desc'], path, SHOTS[d['shot']], data)
    proto = (f' {d["name"]} speaks the {d["proto"]} protocol, so it uses NavQL\'s {d["proto"]} support, '
             f'with the differences handled for you.') if d['kind'] == 'compat' else ''
    facts = ''.join(f'<li><strong>{esc(a)}</strong><span>{esc(b)}</span></li>' for a, b in d['facts'])
    cards = ''.join(f'<article class="card"><div class="bar"></div><h3>{t}</h3><p>{b}</p></article>' for t, b in d['cards'])
    details = ''.join(f'<li>{x}</li>' for x in d['details'])
    notyet = ''.join(f'<li>{x}</li>' for x in d['notyet'])
    out += f'''
<main id="main">
  <section class="page-hero" aria-labelledby="hero-title">
    <div class="wrap">
      <div>
        {crumbs([(n, h) for n, h, _ in trail])}
        <p class="label">NavQL for {d["name"]}</p>
        <h1 id="hero-title">{d["h1"]}</h1>
        <p class="lead">{d["lead"]}</p>
        <div class="actions"><a class="btn btn-primary" href="/#download">Download NavQL</a><a class="btn btn-secondary" href="#features">What it does</a></div>
        <p class="platform-line">Free · macOS (Apple Silicon) · Windows · Linux</p>
      </div>
      <div>{shot(d["shot"])}<p class="shot-caption">{caption(d["shot"], d["name"])}</p></div>
    </div>
  </section>

  <div class="facts"><div class="wrap"><ul>{facts}</ul></div></div>

  <section class="block" id="features" aria-labelledby="features-title">
    <div class="wrap">
      <div class="section-head"><p class="label">What NavQL does with {d["name"]}</p>
        <h2 id="features-title">Built for the way you work with {d["name"]}.</h2>
        <p>Everything below works on {d["name"]} today.{proto}</p></div>
      <div class="cards">{cards}</div>
    </div>
  </section>

  <section class="block alt" aria-labelledby="details-title">
    <div class="wrap split">
      <div>
        <h2 id="details-title" class="label">Also included</h2>
        <h3>The details that save time.</h3>
        <ul class="checks">{details}</ul>
      </div>
      <div>
        <h2 class="label">Not yet</h2>
        <h3>What NavQL does not do on {d["name"]} today.</h3>
        <p class="sub">So you know before you download.</p>
        <ul class="checks neutral">{notyet}</ul>
      </div>
    </div>
  </section>

{faq_block(d["faq"])}{db_links(d["slug"])}{cta(d["name"])}</main>

'''
    return out + tail()


def alt_page(a):
    path = f'/alternatives/{a["slug"]}/'
    title = f'NavQL vs {a["name"]}: a free {a["name"]} alternative'
    trail = [('NavQL', '/', '/'), ('Compare', '/alternatives/', '/alternatives/'), (f'vs {a["name"]}', None, path)]
    data = [{'@context': 'https://schema.org', '@type': 'WebPage', 'name': title, 'url': SITE + path,
             'description': a['desc'], 'inLanguage': 'en', 'dateModified': LASTMOD,
             'about': [{'@type': 'SoftwareApplication', 'name': 'NavQL', 'url': SITE + '/'},
                       {'@type': 'SoftwareApplication', 'name': a['name'], 'url': a['site']}]},
            crumbs_ld(trail), faq_ld(a['faq'])]
    out = head(title, a['desc'], path, SHOTS[a['shot']], data)
    rows = ''.join(f'<tr><th scope="row">{esc(r)}</th><td data-label="NavQL">{esc(n)}</td><td data-label="{esc(a["name"])}">{esc(t)}</td></tr>' for r, n, t in a['rows'])
    them = ''.join(f'<li>{esc(x)}</li>' for x in a['them'])
    us = ''.join(f'<li>{esc(x)}</li>' for x in a['us'])
    others = ''.join(f'<li><a href="/alternatives/{o["slug"]}/"><strong>NavQL vs {o["name"]}</strong><span>Comparison</span></a></li>'
                     for o in ALTS if o['slug'] != a['slug'])
    out += f'''
<main id="main">
  <section class="page-hero" aria-labelledby="hero-title">
    <div class="wrap">
      <div>
        {crumbs([(n, h) for n, h, _ in trail])}
        <p class="label">{esc(a["name"])} alternative</p>
        <h1 id="hero-title">NavQL vs {esc(a["name"])}<span class="hl">.</span></h1>
        <p class="lead">{esc(a["lead"])}</p>
        <div class="actions"><a class="btn btn-primary" href="/#download">Download NavQL</a><a class="btn btn-secondary" href="#compare">See the comparison</a></div>
        <p class="platform-line">Free · macOS (Apple Silicon) · Windows · Linux</p>
      </div>
      <div>{shot(a["shot"])}<p class="shot-caption">{caption(a["shot"])}</p></div>
    </div>
  </section>

  <section class="block" id="compare" aria-labelledby="compare-title">
    <div class="wrap">
      <div class="section-head"><p class="label">Side by side</p><h2 id="compare-title">How they compare.</h2>
        <p>Facts about {esc(a["name"])} come from <a class="inline" href="{a["site"]}" rel="noopener">its website</a>, read on {CHECKED}. “Not listed” means we did not find it there, not that it can never exist; products change, so check their site before you decide.</p></div>
      <div class="table-scroll" role="region" aria-label="NavQL and {esc(a["name"])} compared" tabindex="0">
        <table class="compare">
          <thead><tr><th scope="col">Feature</th><th scope="col">NavQL</th><th scope="col">{esc(a["name"])}</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
      </div>
      <p class="note">Found something out of date? Tell us at <a class="inline" href="https://github.com/navql/releases/issues">github.com/navql/releases/issues</a> and we will fix it.</p>
    </div>
  </section>

  <section class="block alt" aria-labelledby="choose-title">
    <div class="wrap split">
      <div>
        <h2 id="choose-title" class="label">Choose {esc(a["name"])} if</h2>
        <h3>{esc(a["name"])} may be the better pick when…</h3>
        <ul class="checks neutral">{them}</ul>
      </div>
      <div>
        <h2 class="label">Choose NavQL if</h2>
        <h3>NavQL is the better pick when…</h3>
        <ul class="checks">{us}</ul>
      </div>
    </div>
  </section>

  <section class="block" aria-labelledby="only-title">
    <div class="wrap">
      <div class="section-head"><p class="label">Only in NavQL</p><h2 id="only-title">What NavQL brings to the table.</h2></div>
      <div class="cards">{''.join(f'<article class="card"><div class="bar"></div><h3>{t}</h3><p>{b}</p></article>' for t, b in NAVQL_EDGE)}</div>
    </div>
  </section>

{faq_block(a["faq"] + COMMON_ALT_FAQ)}  <section class="block" aria-labelledby="more-title">
    <div class="wrap">
      <div class="section-head"><p class="label">More comparisons</p><h2 id="more-title">NavQL and other clients.</h2></div>
      <ul class="links">{others}</ul>
    </div>
  </section>

{cta()}</main>

'''
    return out + tail()


NAVQL_EDGE = [
    RELATED,
    ('Activity tab',
     'Sessions with their queries and locks, who blocks whom, cancel or end a session, top queries from the server\'s own '
     'statistics, health checks with suggested fixes and server settings, on PostgreSQL, MySQL, MariaDB, SQL Server, '
     'MongoDB, Redis and compatible servers.'),
    ('Backups in one click',
     'pg_dump, mysqldump and mongodump run in the background, stream straight to a file and work through the SSH tunnel. '
     'SQLite uses its own online backup.'),
    BUILDER,
    ('Read only that really is',
     'Read-only connections accept only reading statements. On PostgreSQL and MySQL they also run inside a '
     '<code>READ ONLY</code> transaction, so a CTE with <code>DELETE</code> is refused.'),
    ('Compatible servers by name',
     'CockroachDB, TimescaleDB, Supabase, Neon, TiDB, Valkey and Dragonfly are detected, shown by name and handled where '
     'they differ.'),
]

COMMON_ALT_FAQ = [
    ('Is NavQL really free?',
     'Yes. NavQL is free of charge for personal and commercial work, on any number of your own computers. It is not open source.'),
    ('Where does NavQL keep my passwords?',
     'Only on your computer, encrypted with a key protected by your operating system. NavQL connects directly from your '
     'computer to your databases.'),
]


def hub_page():
    path = '/alternatives/'
    title = 'NavQL compared with TablePlus, DBeaver, DataGrip and more'
    desc = 'Honest comparisons of NavQL with TablePlus, DBeaver, DataGrip, Beekeeper Studio, pgAdmin, Navicat and DB Pro: what each does well.'
    trail = [('NavQL', '/', '/'), ('Compare', None, path)]
    data = [{'@context': 'https://schema.org', '@type': 'CollectionPage', 'name': title, 'url': SITE + path,
             'description': desc, 'inLanguage': 'en', 'dateModified': LASTMOD,
             'hasPart': [{'@type': 'WebPage', 'name': f'NavQL vs {a["name"]}', 'url': f'{SITE}/alternatives/{a["slug"]}/'} for a in ALTS]},
            crumbs_ld(trail)]
    out = head(title, desc, path, SHOTS['diagram-focus'], data)
    items = ''.join(f'<li><a href="/alternatives/{a["slug"]}/"><strong>NavQL vs {a["name"]}</strong><span>{esc(a["lead"].split(". ")[0])}.</span></a></li>' for a in ALTS)
    out += f'''
<main id="main">
  <section class="page-hero" aria-labelledby="hero-title">
    <div class="wrap">
      <div>
        {crumbs([(n, h) for n, h, _ in trail])}
        <p class="label">Compare</p>
        <h1 id="hero-title">How NavQL compares<span class="hl">.</span></h1>
        <p class="lead">Every database client has its strengths. These pages say where another tool is the better pick, and what NavQL adds, using only what each product's own website states.</p>
        <div class="actions"><a class="btn btn-primary" href="/#download">Download NavQL</a><a class="btn btn-secondary" href="#list">See the comparisons</a></div>
      </div>
      <div>{shot('diagram-focus')}<p class="shot-caption">{caption('diagram-focus')}</p></div>
    </div>
  </section>

  <section class="block" id="list" aria-labelledby="list-title">
    <div class="wrap">
      <div class="section-head"><p class="label">Comparisons</p><h2 id="list-title">NavQL and other clients.</h2></div>
      <ul class="links">{items}</ul>
    </div>
  </section>

  <section class="block alt" aria-labelledby="only-title">
    <div class="wrap">
      <div class="section-head"><p class="label">Only in NavQL</p><h2 id="only-title">What NavQL brings to the table.</h2></div>
      <div class="cards">{''.join(f'<article class="card"><div class="bar"></div><h3>{t}</h3><p>{b}</p></article>' for t, b in NAVQL_EDGE)}</div>
    </div>
  </section>

{cta()}</main>

'''
    return out + tail()


def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)


def update_index():
    """The home page keeps its own CSS; only its footer and the database strip links come from here."""
    p = ROOT / 'index.html'
    s = p.read_text()
    s = re.sub(r'<footer[\s\S]*?</footer>\n', lambda _: footer_html(), s, count=1)
    p.write_text(s)


def sitemap():
    urls = ['/'] + [f'/{d["slug"]}/' for d in DATABASES] + ['/alternatives/'] + [f'/alternatives/{a["slug"]}/' for a in ALTS]
    lines = [f'  <url><loc>{SITE}{u}</loc><lastmod>{LASTMOD}</lastmod></url>' for u in urls]
    lines += [f'  <url><loc>{SITE}/privacy.html</loc><lastmod>2026-11-14</lastmod></url>',
              f'  <url><loc>{SITE}/terms.html</loc><lastmod>2026-11-14</lastmod></url>']
    write('sitemap.xml', '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + '\n'.join(lines) + '\n</urlset>\n')


if __name__ == '__main__':
    for d in DATABASES:
        write(f'{d["slug"]}/index.html', db_page(d))
    for a in ALTS:
        write(f'alternatives/{a["slug"]}/index.html', alt_page(a))
    write('alternatives/index.html', hub_page())
    update_index()
    sitemap()
    print(f'{len(DATABASES)} database pages, {len(ALTS)} comparisons, hub, footer, sitemap')
