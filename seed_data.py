"""
Seed script — populates categories, exams, and 100 questions.
Run: python seed_data.py
"""
from app import app
from models import db, User, Category, Exam, Question
from werkzeug.security import generate_password_hash


QUESTIONS = {
    'Networking': [
        ('Which protocol is connection-oriented?', 'UDP', 'TCP', 'ICMP', 'ARP', 'B'),
        ('What does DNS stand for?', 'Dynamic Network Service', 'Domain Name System', 'Data Network Server', 'Digital Naming System', 'B'),
        ('Which layer of OSI handles routing?', 'Data Link', 'Network', 'Transport', 'Session', 'B'),
        ('What is the default port for HTTPS?', '80', '8080', '443', '22', 'C'),
        ('Which device connects two different networks?', 'Hub', 'Switch', 'Router', 'Repeater', 'C'),
        ('What does IP stand for?', 'Internet Provider', 'Internet Protocol', 'Internal Process', 'Interface Port', 'B'),
        ('Which is a private IP range?', '8.8.8.0', '192.168.0.0/16', '1.1.1.0', '200.200.200.0', 'B'),
        ('What does MAC address identify?', 'Network layer', 'Physical device', 'Application', 'Session', 'B'),
        ('Which protocol resolves IP to MAC?', 'DNS', 'DHCP', 'ARP', 'RARP', 'C'),
        ('What is subnet mask 255.255.255.0 in CIDR?', '/16', '/24', '/32', '/8', 'B'),
        ('Which topology uses a central hub?', 'Ring', 'Star', 'Mesh', 'Bus', 'B'),
        ('Port 22 is used by which protocol?', 'FTP', 'SSH', 'Telnet', 'SMTP', 'B'),
        ('What does DHCP do?', 'Resolve names', 'Assign IP addresses', 'Encrypt traffic', 'Route packets', 'B'),
        ('Which cable supports highest speed?', 'Cat5', 'Cat5e', 'Cat6a', 'Cat3', 'C'),
        ('What is the loopback address?', '192.168.0.1', '10.0.0.1', '127.0.0.1', '0.0.0.0', 'C'),
        ('Which OSI layer does TCP belong to?', 'Network', 'Transport', 'Session', 'Data Link', 'B'),
        ('What is a VLAN?', 'Virtual LAN', 'Very Large Area Network', 'Variable Length Access Node', 'Virtual Link Access', 'A'),
        ('What does NAT do?', 'Assigns MACs', 'Translates IP addresses', 'Encrypts data', 'Routes domains', 'B'),
        ('Which protocol sends email?', 'POP3', 'IMAP', 'SMTP', 'FTP', 'C'),
        ('What is latency measured in?', 'Bytes', 'Milliseconds', 'Hertz', 'Bits', 'B'),
    ],
    'Programming': [
        ('What does OOP stand for?', 'Object-Oriented Programming', 'Open Operation Protocol', 'Object Orientation Process', 'Online Operating Program', 'A'),
        ('Which is NOT a Python data type?', 'list', 'tuple', 'dict', 'array', 'D'),
        ('What is time complexity of binary search?', 'O(n)', 'O(log n)', 'O(n²)', 'O(1)', 'B'),
        ('Which keyword defines a function in Python?', 'func', 'def', 'function', 'lambda', 'B'),
        ('What does HTML stand for?', 'HyperText Markup Language', 'HighText Machine Language', 'HyperTool Markup Language', 'HomeTool Markup Language', 'A'),
        ('What does an IDE provide?', 'Only text editing', 'Only debugging', 'Code editing, debugging, and tools', 'Only compilation', 'C'),
        ('What is a variable?', 'A fixed value', 'A named storage', 'A function', 'A class', 'B'),
        ('Which loop always runs at least once?', 'for', 'while', 'do-while', 'foreach', 'C'),
        ('What is recursion?', 'A loop', 'A function calling itself', 'A variable', 'An array', 'B'),
        ('What does API stand for?', 'Applied Programming Interface', 'Application Programming Interface', 'Application Process Integration', 'Applied Process Interface', 'B'),
        ('Which is a compiled language?', 'Python', 'JavaScript', 'C++', 'Ruby', 'C'),
        ('What is a stack?', 'FIFO', 'LIFO', 'Random', 'Sorted', 'B'),
        ('What is Git used for?', 'Design', 'Version control', 'Database', 'Compilation', 'B'),
        ('What is a bug?', 'A feature', 'An error in code', 'A loop', 'A variable', 'B'),
        ('What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'System Query Logic', 'Standard Question Language', 'A'),
        ('Which symbol starts a comment in Python?', '//', '#', '/*', '--', 'B'),
        ('What is an algorithm?', 'A program', 'A step-by-step procedure', 'A variable', 'A file', 'B'),
        ('What is JSON?', 'A programming language', 'A data format', 'A database', 'A server', 'B'),
        ("What does DRY stand for?", 'Do Repeat Yourself', "Don't Repeat Yourself", 'Data Reuse Yield', 'Dynamic Runtime', 'B'),
        ('Which data structure uses keys and values?', 'List', 'Tuple', 'Dictionary', 'Set', 'C'),
    ],
    'Database': [
        ('What does SQL stand for?', 'Structured Query Language', 'Simple Query Language', 'Standard Query Logic', 'System Query Language', 'A'),
        ('Which is a primary key?', 'Duplicates allowed', 'Unique identifier', 'Optional field', 'Foreign key', 'B'),
        ('What does ACID stand for?', 'Atomicity, Consistency, Isolation, Durability', 'Atomic, Concise, Integrated, Durable', 'All, Commit, Index, Data', 'None', 'A'),
        ('Which SQL command retrieves data?', 'INSERT', 'SELECT', 'UPDATE', 'DELETE', 'B'),
        ('What is a foreign key?', 'Primary key', 'References another table', 'Index', 'View', 'B'),
        ('Which JOIN returns all rows from both tables?', 'INNER', 'LEFT', 'RIGHT', 'FULL OUTER', 'D'),
        ('What is normalization?', 'Adding duplicates', 'Organizing data to reduce redundancy', 'Deleting tables', 'Encryption', 'B'),
        ('Which is a NoSQL database?', 'MySQL', 'PostgreSQL', 'MongoDB', 'Oracle', 'C'),
        ('What does GROUP BY do?', 'Sorts', 'Aggregates', 'Filters', 'Joins', 'B'),
        ('Which command removes a table?', 'DELETE', 'DROP', 'REMOVE', 'TRUNCATE', 'B'),
        ('What is an index used for?', 'Slowing queries', 'Speeding lookups', 'Encryption', 'Storage', 'B'),
        ('Which is a DDL command?', 'SELECT', 'CREATE', 'INSERT', 'UPDATE', 'B'),
        ('What does WHERE do?', 'Groups', 'Filters rows', 'Sorts', 'Joins', 'B'),
        ('What is a view?', 'Physical table', 'Virtual table from a query', 'Index', 'Backup', 'B'),
        ('Which SQL function counts rows?', 'SUM', 'AVG', 'COUNT', 'MAX', 'C'),
        ('What is a transaction?', 'A single query', 'A group of queries as a unit', 'A table', 'An index', 'B'),
        ('What does COMMIT do?', 'Undoes changes', 'Saves changes', 'Deletes data', 'Sorts data', 'B'),
        ('Which is a relational DBMS?', 'MongoDB', 'PostgreSQL', 'Redis', 'Cassandra', 'B'),
        ('What is a stored procedure?', 'A table', 'Precompiled SQL code', 'An index', 'A view', 'B'),
        ('What does HAVING do?', 'Filters rows', 'Filters groups', 'Joins', 'Sorts', 'B'),
    ],
    'Operating Systems': [
        ('What is an OS?', 'A program', 'System software managing hardware', 'A game', 'A browser', 'B'),
        ('Which is not an OS?', 'Windows', 'Linux', 'MacOS', 'Photoshop', 'D'),
        ('What is a process?', 'A file', 'A program in execution', 'A folder', 'A thread', 'B'),
        ('What is virtual memory?', 'RAM', 'Disk space used as RAM', 'Cache', 'ROM', 'B'),
        ('Which scheduling is FIFO?', 'Round Robin', 'First Come First Serve', 'Priority', 'Shortest Job', 'B'),
        ('What is a deadlock?', 'A process finish', 'Two processes waiting on each other', 'An error', 'A thread', 'B'),
        ('What does GUI stand for?', 'General User Interface', 'Graphical User Interface', 'Global User Interaction', 'Graphic Utility Interface', 'B'),
        ('Which is a kernel type?', 'Monolithic', 'Interpreter', 'Compiler', 'Virtual', 'A'),
        ('What is paging?', 'Memory management', 'Disk format', 'Networking', 'Compilation', 'A'),
        ('What is a thread?', 'A process', 'Lightweight process', 'A file', 'An OS', 'B'),
        ('What does CPU stand for?', 'Central Processing Unit', 'Computer Personal Unit', 'Central Program Utility', 'Core Process Unit', 'A'),
        ('What is a system call?', 'A function call', 'Interface to kernel', 'A program', 'A file', 'B'),
        ('Which is a real-time OS?', 'Windows', 'Linux', 'VxWorks', 'MacOS', 'C'),
        ('What is thrashing?', 'High CPU use', 'Excessive paging', 'Crashed process', 'Memory leak', 'B'),
        ('What is a semaphore?', 'A variable', 'A synchronization tool', 'A file', 'A thread', 'B'),
        ('What does BIOS do?', 'Boots system', 'Browses web', 'Compiles code', 'Edits files', 'A'),
        ('What is a file system?', 'A file', 'A method to organize files', 'A folder', 'An OS', 'B'),
        ('Which is a Linux file system?', 'NTFS', 'ext4', 'FAT32', 'exFAT', 'B'),
        ('What is a context switch?', 'Changing files', 'Switching CPU between processes', 'Booting', 'Formatting', 'B'),
        ('What is multiprogramming?', 'Multiple CPUs', 'Multiple programs in memory', 'Multiple users', 'Multiple files', 'B'),
    ],
    'Web Development': [
        ('What does HTML stand for?', 'HyperText Markup Language', 'HighText Machine Language', 'HyperTool Markup Language', 'HomeTool Markup Language', 'A'),
        ('Which is a CSS framework?', 'Django', 'Flask', 'Bootstrap', 'React', 'C'),
        ('What does JS stand for?', 'Java Source', 'JavaScript', 'Just Script', 'Joint Script', 'B'),
        ('Which tag creates a hyperlink?', '<link>', '<a>', '<href>', '<url>', 'B'),
        ('What is REST?', 'A protocol', 'An architectural style for APIs', 'A database', 'A language', 'B'),
        ('What does HTTP status 404 mean?', 'Server error', 'Not found', 'OK', 'Redirect', 'B'),
        ('Which is a frontend framework?', 'Flask', 'Django', 'React', 'Node', 'C'),
        ('What is a cookie?', 'A file', 'Small data stored in browser', 'A server', 'A protocol', 'B'),
        ('What does CSS stand for?', 'Cascading Style Sheets', 'Computer Style Sheets', 'Creative Style System', 'Cascading System Style', 'A'),
        ('Which method submits a form?', 'GET', 'POST', 'PUT', 'Any', 'B'),
        ('What is JSON?', 'A language', 'A data format', 'A database', 'A server', 'B'),
        ('Which is a backend language?', 'HTML', 'CSS', 'Python', 'Bootstrap', 'C'),
        ('What is HTTPS?', 'Secure HTTP', 'High HTTP', 'Hyper HTTP', 'Host HTTP', 'A'),
        ('Which is a version control system?', 'Git', 'Docker', 'Nginx', 'Apache', 'A'),
        ('What is AJAX?', 'A language', 'Async JS and XML', 'A framework', 'A server', 'B'),
        ('Which CSS property changes text color?', 'font-color', 'color', 'text-color', 'fg-color', 'B'),
        ('What is responsive design?', 'Fast site', 'Site adapting to screens', 'Secure site', 'Small site', 'B'),
        ('What is CORS?', 'Cross-Origin Resource Sharing', 'Core Object Render System', 'Cross Object Request System', 'Cache Object Resource System', 'A'),
        ('Which port is default for HTTP?', '443', '80', '8080', '22', 'B'),
        ('What is a CDN?', 'Content Delivery Network', 'Central Data Node', 'Core Development Network', 'Code Delivery Node', 'A'),
    ],
}


def seed():
    with app.app_context():
        db.create_all()

        # --- Admin ---
        if not User.query.filter_by(is_admin=True).first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            print('✅ Admin created: admin / admin123')

        # --- Categories ---
        icon_map = {
            'Networking': '🌐',
            'Programming': '💻',
            'Database': '🗄️',
            'Operating Systems': '🖥️',
            'Web Development': '🌍',
        }
        description_map = {
            'Networking': 'Protocols, IP addressing, OSI model, and network devices.',
            'Programming': 'Data structures, algorithms, OOP, and coding basics.',
            'Database': 'SQL, normalization, transactions, and database design.',
            'Operating Systems': 'Processes, memory, scheduling, and system calls.',
            'Web Development': 'HTML, CSS, JavaScript, APIs, and modern web.',
        }

        for cat_name in QUESTIONS.keys():
            if not Category.query.filter_by(name=cat_name).first():
                db.session.add(Category(
                    name=cat_name,
                    description=description_map[cat_name],
                    icon=icon_map[cat_name]
                ))
        db.session.commit()
        print('✅ Categories created')

        # --- Exams + Questions ---
        for cat_name, qs in QUESTIONS.items():
            cat = Category.query.filter_by(name=cat_name).first()
            exam_title = f'{cat_name} — Intermediate Exam'
            exam = Exam.query.filter_by(title=exam_title).first()

            if not exam:
                exam = Exam(
                    title=exam_title,
                    description=f'Intermediate {cat_name} exam. 50 questions selected at random from a pool of {len(qs)}.',
                    duration_minutes=60,
                    category_id=cat.id,
                    questions_per_attempt=50
                )
                db.session.add(exam)
                db.session.commit()
                print(f'✅ Exam created: {exam_title}')

                for (text, a, b, c, d, correct) in qs:
                    db.session.add(Question(
                        exam_id=exam.id,
                        text=text,
                        option_a=a,
                        option_b=b,
                        option_c=c,
                        option_d=d,
                        correct_answer=correct
                    ))
                db.session.commit()
                print(f'   └─ {len(qs)} questions added')

        print('\n🎉 Seeding complete!')
        print('   Admin login: admin / admin123')


if __name__ == '__main__':
    seed()