import json
from datetime import datetime, date
from app import create_app
from extensions import db
from models.company import Company, JobRole
from models.assessment import Question, Assessment, AssessmentQuestion

def seed_rich_data():
    app = create_app()
    with app.app_context():
        print("1. Seeding 20+ Diverse Companies across Global Tech, Product, Sales, and Pharma...")
        
        companies_data = [
            # Global Tech MNCs
            ("TCS (Tata Consultancy Services)", "Global Tech MNCs", "Tier 1 Service", "https://www.tcs.com", "Global enterprise IT, cloud solutions, and systems consulting for Fortune 500."),
            ("Infosys Limited", "Global Tech MNCs", "Tier 1 Service", "https://www.infosys.com", "Next-generation digital services and consulting across cloud, AI, and enterprise architectures."),
            ("Wipro Technologies", "Global Tech MNCs", "Tier 1 Service", "https://www.wipro.com", "Pioneering IT consulting and business process services spanning 6 continents."),
            ("Cognizant Technology Solutions", "Global Tech MNCs", "Tier 1 Service", "https://www.cognizant.com", "Engineering modern businesses through digital products, cloud, and analytics."),
            ("Accenture", "Global Tech MNCs", "Global Consulting & Tech", "https://www.accenture.com", "World-leading professional services in strategy, consulting, digital, and technology."),
            ("Microsoft", "Global Tech MNCs", "Product & Big Tech", "https://www.microsoft.com", "Global technology pioneer in Windows, Azure cloud, enterprise software, and OpenAI tools."),
            ("Amazon", "Global Tech MNCs", "Product & Big Tech", "https://www.amazon.jobs", "Global leader in e-commerce, cloud infrastructure (AWS), logistics, and digital streaming."),
            ("Google", "Global Tech MNCs", "Product & Big Tech", "https://careers.google.com", "Innovator in global search, Google Cloud, distributed systems, Android, and AI models."),
            ("Capgemini", "Global Tech MNCs", "Tier 1 Service", "https://www.capgemini.com", "Global leader in partnering with companies to transform and manage business through tech."),
            ("IBM", "Global Tech MNCs", "Enterprise Tech & Cloud", "https://www.ibm.com", "Hybrid cloud, artificial intelligence (Watson), and enterprise hardware/software."),

            # Product & Fintech
            ("Razorpay", "Product & Fintech", "Product & Unicorn", "https://razorpay.com", "Leading full-stack financial services and digital payment infrastructure in India."),
            ("Zerodha", "Product & Fintech", "Product & Fintech", "https://zerodha.com", "India's largest retail stock broker and algorithmic trading platform pioneer."),
            ("Flipkart", "Product & Fintech", "E-Commerce & Product", "https://www.flipkartcareers.com", "Pioneering Indian e-commerce platform with ultra-scale logistics and backend microservices."),
            ("Paytm (One97 Communications)", "Product & Fintech", "Product & Fintech", "https://paytm.com", "Digital payments, QR technology, banking, and merchant lending ecosystem."),
            ("Adobe", "Product & Fintech", "Global Product Leader", "https://www.adobe.com", "World leader in creative software, digital experiences, PDF standards, and document cloud."),
            ("Swiggy", "Product & Fintech", "Product & Quick Commerce", "https://www.swiggy.com", "On-demand convenience platform offering food delivery and Instamart quick commerce."),

            # Sales, Consulting & Management
            ("Deloitte", "Sales, Consulting & Management", "Big 4 Consulting", "https://www.deloitte.com", "Audit, consulting, financial advisory, risk management, and tax services."),
            ("McKinsey & Company", "Sales, Consulting & Management", "Management Consulting", "https://www.mckinsey.com", "Global management consulting firm advising top corporate, government, and NGO leaders."),
            ("Ernst & Young (EY)", "Sales, Consulting & Management", "Big 4 Advisory", "https://www.ey.com", "Building a better working world through assurance, consulting, strategy, and transactions."),
            ("PwC (PricewaterhouseCoopers)", "Sales, Consulting & Management", "Big 4 Consulting", "https://www.pwc.com", "Delivering quality in assurance, advisory, and tax professional services globally."),
            ("HDFC Bank", "Sales, Consulting & Management", "Banking & Financial Services", "https://www.hdfcbank.com", "Leading Indian private sector bank offering investment banking, retail, and corporate sales."),
            ("Zomato Sales & Enterprise", "Sales, Consulting & Management", "Corporate Sales & Growth", "https://www.zomato.com", "Enterprise restaurant partnerships, B2B Hyperpure sales, and advertising solutions."),

            # Pharmaceutical & Healthcare
            ("Sun Pharmaceutical Industries", "Pharmaceutical & Healthcare", "Pharma & Healthcare Leader", "https://www.sunpharma.com", "India's largest pharmaceutical company with specialty medicines and active ingredients."),
            ("Cipla Limited", "Pharmaceutical & Healthcare", "Pharma & Therapeutics", "https://www.cipla.com", "Global pharmaceutical company focused on respiratory therapeutics, oncology, and antiretrovirals."),
            ("Dr. Reddy's Laboratories", "Pharmaceutical & Healthcare", "Pharma & Biosimilars", "https://www.drreddys.com", "Multinational pharmaceutical firm manufacturing generics, active ingredients, and proprietary products."),
            ("Pfizer", "Pharmaceutical & Healthcare", "Global Bio-Pharma", "https://www.pfizer.com", "Global bio-pharmaceutical corporation delivering vaccines, oncology, and rare disease breakthroughs."),
            ("Biocon", "Pharmaceutical & Healthcare", "Biotechnology & Biologics", "https://www.biocon.com", "Pioneering Indian biopharmaceutical company developing biosimilars and insulins.")
        ]

        for name, industry, tier, web, desc in companies_data:
            existing = Company.query.filter_by(name=name).first()
            if not existing:
                comp = Company(
                    name=name,
                    industry=industry,
                    tier=tier,
                    website=web,
                    careers_url=web,
                    description=desc,
                    is_verified=True,
                    last_verified_date=date.today()
                )
                db.session.add(comp)
                db.session.flush()

                # Add sample default entry role
                if industry == "Global Tech MNCs":
                    role_title = "Systems Engineer / Software Developer"
                    ctc = "4.0 - 9.0 LPA"
                elif industry == "Product & Fintech":
                    role_title = "Software Engineer - Backend / Frontend"
                    ctc = "12.0 - 24.0 LPA"
                elif industry == "Sales, Consulting & Management":
                    role_title = "Associate Business Analyst / Management Trainee"
                    ctc = "6.5 - 14.0 LPA"
                else:
                    role_title = "Executive Trainee - Quality Assurance / Formulation"
                    ctc = "4.5 - 7.5 LPA"

                db.session.add(JobRole(
                    company_id=comp.id,
                    title=role_title,
                    description=f"Entry role at {name} for university graduates.",
                    ctc_range=ctc,
                    min_cgpa=6.5
                ))
            else:
                existing.industry = industry
                existing.tier = tier
                existing.description = desc

        db.session.commit()
        print("Companies successfully seeded!")

        print("2. Seeding 25+ Comprehensive Practice Questions across Tech, Math, Aptitude & Domain...")
        
        questions_data = [
            # PYTHON
            (
                "Python", "Core Internals", "Easy",
                "What is the output of the Python expression: `[x**2 for x in range(5) if x % 2 == 1]`?",
                ["[0, 1, 4, 9, 16]", "[1, 9]", "[1, 4, 9]", "[0, 4, 16]"],
                1,
                "range(5) gives 0, 1, 2, 3, 4. The odd numbers are 1 and 3. Their squares are 1**2 = 1 and 3**2 = 9. Output is [1, 9]."
            ),
            (
                "Python", "Memory & Functions", "Medium",
                "Why is using a mutable default argument like `def add_item(item, lst=[])` dangerous in Python?",
                [
                    "It causes a SyntaxError at compile time",
                    "The default list is created once at function definition, retaining state across successive calls",
                    "It consumes excessive GPU memory during execution",
                    "Python automatically deletes mutable default arguments after one run"
                ],
                1,
                "In Python, default arguments are evaluated only once when the function definition is executed, so the same list instance is shared across all calls that omit the argument."
            ),
            (
                "Python", "Concurrency", "Hard",
                "What is the primary role of the Global Interpreter Lock (GIL) in standard CPython?",
                [
                    "To prevent parallel execution of multiple processes on multi-core systems",
                    "A mutex that protects access to Python objects, preventing multiple threads from executing Python bytecodes at once",
                    "To speed up disk I/O operations by locking CPU registers",
                    "To automatically garbage collect circular references in O(1) time"
                ],
                1,
                "The CPython GIL is a mutual exclusion lock used by the CPython memory management which ensures that only one native thread executes Python bytecode at any given moment."
            ),

            # JAVA & OOPS
            (
                "Java", "OOP Principles", "Easy",
                "Which OOP concept is demonstrated when a subclass provides a specific implementation of a method that is already defined in its superclass?",
                ["Method Overloading", "Method Overriding (Runtime Polymorphism)", "Data Hiding", "Tight Coupling"],
                1,
                "Method Overriding occurs when a child class implements a method with the same name, return type, and signature as defined in its parent class."
            ),
            (
                "Java", "Collections Internals", "Medium",
                "In Java 8+, what happens when the number of items in a single bucket of a HashMap exceeds TREEIFY_THRESHOLD (default 8)?",
                [
                    "An OutOfMemoryError is thrown",
                    "The bucket linked list is converted into a Red-Black balanced Binary Search Tree",
                    "The HashMap automatically deletes the oldest entry",
                    "The bucket size is doubled and all keys are hashed to SHA-256"
                ],
                1,
                "Java 8 optimizes HashMap bucket collisions: when bucket collision chain exceeds 8 and total capacity >= 64, it converts the linked list to a balanced Red-Black Tree, improving lookup from O(n) to O(log n)."
            ),
            (
                "Java", "Core Language", "Medium",
                "Why are `String` objects immutable in Java?",
                [
                    "For security, synchronization thread-safety, HashCode caching, and String Pool reusability",
                    "Because Java does not support heap memory allocation",
                    "To prevent JVM garbage collector from collecting strings",
                    "It was a temporary bug in Java 1.0 that could not be changed"
                ],
                0,
                "Immutability allows String Pool sharing, guarantees that strings cannot be tampered with in network/security sockets, makes them inherently thread-safe, and allows caching of their hashCode."
            ),

            # DATA STRUCTURES & ALGORITHMS
            (
                "DSA", "Sorting Algorithms", "Medium",
                "What is the worst-case time complexity of QuickSort, and when does it occur?",
                [
                    "O(n log n), when the array is randomly shuffled",
                    "O(n^2), when the pivot chosen is always the smallest or largest element (e.g. sorted array with first element as pivot)",
                    "O(n), when all elements are unique",
                    "O(log n), when using dual-pivot partitioning"
                ],
                1,
                "QuickSort degrades to O(n^2) when each partition step divides the array into subproblems of size 0 and n-1, which occurs on sorted arrays if the first or last element is chosen as pivot."
            ),
            (
                "DSA", "Binary Search Trees", "Easy",
                "Which tree traversal method visits a Binary Search Tree (BST) in strictly sorted ascending numerical order?",
                ["Pre-order Traversal", "In-order Traversal (Left, Root, Right)", "Post-order Traversal", "Level-order (BFS) Traversal"],
                1,
                "In a BST, all left child keys < root key < right child keys. In-order traversal visits Left Subtree, then Root, then Right Subtree, resulting in sorted output."
            ),
            (
                "DSA", "Stacks & Parsing", "Medium",
                "Which data structure is the most optimal for validating balanced brackets in expressions like `{[()]}`?",
                ["Queue (FIFO)", "Stack (LIFO)", "Binary Heap", "Hash Table"],
                1,
                "A Stack (Last In, First Out) is ideal because the last opened bracket must always match the first closing bracket encountered."
            ),
            (
                "DSA", "Dynamic Programming", "Hard",
                "What are the two mandatory properties a problem must possess to be solvable via Dynamic Programming?",
                [
                    "Greedy Choice Property and Polynomial Time verification",
                    "Optimal Substructure and Overlapping Subproblems",
                    "Divide and Conquer with independent subproblems",
                    "Asymptotic Upper Bound and Graph acyclicity"
                ],
                1,
                "Dynamic Programming requires: 1) Optimal Substructure (optimal solution contains optimal sub-solutions) and 2) Overlapping Subproblems (the same subproblems are solved repeatedly)."
            ),

            # SQL & DATABASES
            (
                "SQL", "Joins", "Easy",
                "What is the key difference between an `INNER JOIN` and a `LEFT JOIN`?",
                [
                    "INNER JOIN returns all rows from left table; LEFT JOIN only matching rows",
                    "INNER JOIN returns only matching rows from both tables; LEFT JOIN returns all rows from the left table plus matching rows from the right table",
                    "LEFT JOIN is faster because it does not check foreign key constraints",
                    "INNER JOIN can only be used on numerical primary keys"
                ],
                1,
                "INNER JOIN yields only records having matching keys in both tables. LEFT JOIN yields every row from the left table, padding NULLs where no right table match exists."
            ),
            (
                "SQL", "Aggregations", "Medium",
                "In a SQL query, what is the exact execution difference between `WHERE` and `HAVING` clauses?",
                [
                    "WHERE filters individual rows before aggregation; HAVING filters aggregated groups after GROUP BY",
                    "HAVING executes first, then WHERE filters the result table",
                    "WHERE only works with subqueries, while HAVING only works with views",
                    "They are exact synonyms in ANSI SQL standard"
                ],
                0,
                "The WHERE clause applies condition filters to individual records before grouping occurs. The HAVING clause applies condition filters to aggregated metric groups (like COUNT, SUM, AVG)."
            ),
            (
                "SQL", "Performance & Indexing", "Medium",
                "How does a B-Tree index on a relational database column accelerate `SELECT * FROM users WHERE email = ?` queries?",
                [
                    "It caches the entire table in CPU L1 cache",
                    "It reduces search time from a full table scan O(N) to balanced logarithmic search O(log N)",
                    "It converts relational data into an in-memory document database",
                    "It compresses duplicate email strings using Gzip"
                ],
                1,
                "A B-Tree index maintains keys in a balanced tree structure, allowing the database engine to find the target row in O(log N) page reads instead of scanning all N table rows."
            ),

            # QUANTITATIVE APTITUDE & MATH
            (
                "Aptitude", "Speed & Distance", "Easy",
                "A train 180 meters long is traveling at a speed of 54 km/h. How many seconds will it take to pass a stationary signal pole?",
                ["8 seconds", "10 seconds", "12 seconds", "15 seconds"],
                2,
                "Speed in m/s = 54 * (5/18) = 15 m/s. Time to clear pole = Distance / Speed = 180 / 15 = 12 seconds."
            ),
            (
                "Aptitude", "Time & Work", "Medium",
                "Person A can complete a project in 12 days, and Person B can complete it in 24 days. If they collaborate together, how many days will the project take?",
                ["6 days", "8 days", "10 days", "9 days"],
                1,
                "A's 1-day work = 1/12. B's 1-day work = 1/24. Combined 1-day work = 1/12 + 1/24 = 3/24 = 1/8. Total time = 8 days."
            ),
            (
                "Aptitude", "Percentages & Profit", "Easy",
                "A merchant purchases an item for $800 and sells it for $1,000. What is the merchant's percentage profit on the cost price?",
                ["20%", "25%", "15%", "30%"],
                1,
                "Profit = $1,000 - $800 = $200. Profit Percentage = (Profit / Cost Price) * 100 = (200 / 800) * 100 = 25%."
            ),
            (
                "Aptitude", "Probability", "Medium",
                "If two fair 6-sided dice are rolled simultaneously, what is the exact probability that the sum of the faces equals 7?",
                ["1/12", "1/6", "5/36", "7/36"],
                1,
                "Total outcomes = 6 * 6 = 36. Outcomes summing to 7 are: (1,6), (2,5), (3,4), (4,3), (5,2), (6,1) -> 6 outcomes. Probability = 6/36 = 1/6."
            ),
            (
                "Aptitude", "Permutations & Combinations", "Hard",
                "In how many distinct ways can a student committee of 3 members be selected from a cohort of 8 eligible candidates?",
                ["24", "56", "336", "120"],
                1,
                "Formula is 8C3 = 8! / (3! * 5!) = (8 * 7 * 6) / (3 * 2 * 1) = 336 / 6 = 56 ways."
            ),

            # LOGICAL REASONING
            (
                "Logical", "Series Completion", "Easy",
                "Identify the missing number in the sequence: `2, 6, 12, 20, 30, ?`",
                ["40", "42", "44", "46"],
                1,
                "Differences between successive terms are +4, +6, +8, +10. The next difference must be +12. 30 + 12 = 42. (Alternatively: n*(n+1) -> 1*2, 2*3, 3*4, 4*5, 5*6, 6*7=42)."
            ),
            (
                "Logical", "Coding-Decoding", "Medium",
                "In a certain code language, if 'TECH' is encoded as 'VGEJ', how is 'DATA' encoded under the same rule?",
                ["FCVC", "ECUC", "FCVB", "GBWB"],
                0,
                "Rule: Each letter shifted by +2 in the alphabet. D(+2)->F, A(+2)->C, T(+2)->V, A(+2)->C. Result: FCVC."
            ),
            (
                "Logical", "Syllogisms", "Medium",
                "Statements: 1) All developers are engineers. 2) All engineers are problem solvers. Conclusion: Which is unconditionally true?",
                [
                    "All problem solvers are developers",
                    "All developers are problem solvers",
                    "No engineers are developers",
                    "Some problem solvers are not engineers"
                ],
                1,
                "Transitive logic: If A is a subset of B, and B is a subset of C, then every A is inherently a C. Thus, all developers are problem solvers."
            ),

            # PHARMACEUTICAL & HEALTHCARE (B.Pharma / Life Sciences)
            (
                "Pharmacy", "Pharmacology & Kinetics", "Medium",
                "What does the term 'Bioavailability' (F) quantify in pharmaceutical science?",
                [
                    "The rate of drug excretion through renal kidneys",
                    "The fraction of an administered unchanged drug dose that reaches systemic circulation",
                    "The shelf life of an antibiotic tablet at room temperature",
                    "The total toxicity index in animal clinical models"
                ],
                1,
                "Bioavailability refers to the fraction of an unchanged active drug that successfully enters systemic blood circulation following administration (100% for IV injection)."
            ),
            (
                "Pharmacy", "Clinical Trials", "Hard",
                "Which clinical trial phase is primarily designed to assess drug efficacy and optimal dosage in a small cohort (100-300) of affected patients?",
                ["Phase 0 (Microdosing)", "Phase 1 (Healthy Volunteers Safety)", "Phase 2 (Therapeutic Exploratory Efficacy)", "Phase 4 (Post-Marketing Surveillance)"],
                2,
                "Phase 2 clinical trials focus on evaluating the efficacy of the drug in patients diagnosed with the target condition, while identifying dose response and common short-term side effects."
            ),

            # BUSINESS & MANAGEMENT (MBA / BBA / Consulting)
            (
                "Business", "Financial Valuation", "Medium",
                "How is Return on Investment (ROI) calculated in corporate strategy?",
                [
                    "[(Net Profit / Cost of Investment) * 100]",
                    "[(Gross Revenue / Total Shares) * 100]",
                    "[(Operating Expenses - Taxes) / 12]",
                    "[(Debt / Total Equity) * 100]"
                ],
                0,
                "ROI is a standard profitability ratio calculated as: (Net Profit / Initial Cost of Investment) * 100."
            ),
            (
                "Business", "Operations & Management", "Easy",
                "In agile product management, what is a 'Sprint Retrospective' held for?",
                [
                    "To demonstrate features to the CEO for immediate bonus allocation",
                    "For the cross-functional team to reflect on past sprint workflow, successes, and continuously improve team processes",
                    "To assign disciplinary penalties for unfinished code commits",
                    "To immediately rewrite all database schemas"
                ],
                1,
                "Sprint Retrospectives provide dedicated time for the Scrum team to inspect their process, collaboration, and tools, and identify concrete action items for the upcoming sprint."
            )
        ]

        created_questions = []
        for cat, topic, diff, text, opts, corr, expl in questions_data:
            existing = Question.query.filter_by(question_text=text).first()
            if not existing:
                q = Question(
                    category=cat,
                    sub_topic=topic,
                    difficulty=diff,
                    question_text=text,
                    options_json=json.dumps(opts),
                    correct_option=corr,
                    explanation=expl
                )
                db.session.add(q)
                db.session.flush()
                created_questions.append(q)
            else:
                created_questions.append(existing)

        db.session.commit()
        print(f"Total questions available: {len(created_questions)}")

        # Ensure Practice Assessments exist
        dsa_test = Assessment.query.filter_by(title="DSA & Programming Diagnostic Assessment").first()
        if not dsa_test:
            dsa_test = Assessment(
                title="DSA & Programming Diagnostic Assessment",
                category="DSA",
                duration_minutes=25,
                passing_score=60,
                total_marks=100
            )
            db.session.add(dsa_test)
            db.session.flush()

            # Attach first 10 technical questions
            tech_qs = [q for q in created_questions if q.category in ['DSA', 'Python', 'Java', 'SQL']][:10]
            for q in tech_qs:
                db.session.add(AssessmentQuestion(assessment_id=dsa_test.id, question_id=q.id, points=10))

        apt_test = Assessment.query.filter_by(title="Campus Aptitude & Quantitative Sprint").first()
        if not apt_test:
            apt_test = Assessment(
                title="Campus Aptitude & Quantitative Sprint",
                category="Aptitude",
                duration_minutes=20,
                passing_score=60,
                total_marks=100
            )
            db.session.add(apt_test)
            db.session.flush()

            # Attach aptitude & logical questions
            apt_qs = [q for q in created_questions if q.category in ['Aptitude', 'Logical', 'Business']][:8]
            for q in apt_qs:
                db.session.add(AssessmentQuestion(assessment_id=apt_test.id, question_id=q.id, points=12))

        db.session.commit()
        print("Practice Assessments configured!")
        print("Data Seeding Complete: 25+ Questions & 20+ Companies Ready!")

if __name__ == '__main__':
    seed_rich_data()
