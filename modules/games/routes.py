from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from extensions import db
from services.activity_service import log_activity

games_bp = Blueprint('games', __name__, url_prefix='/games')

# Complete list of 21 interactive educational mind-fresh games
GAMES_CATALOG = [
    # Category 1: Code & Dev Logic (8 Games)
    {
        "id": "binary_search",
        "title": "Binary Search Matrix Guess",
        "category": "Code & Dev Logic",
        "icon": "bi-search",
        "color": "primary",
        "desc": "Find the secret target between 1 and 100 in minimum Log2(N) steps using High/Low clues.",
        "difficulty": "Easy",
        "plays": 1420
    },
    {
        "id": "big_o_battle",
        "title": "Big-O Complexity Speed Battle",
        "category": "Code & Dev Logic",
        "icon": "bi-speedometer2",
        "color": "success",
        "desc": "Pick which asymptotic time complexity wins in speed: O(1), O(log N), O(N), O(N log N), or O(N^2).",
        "difficulty": "Medium",
        "plays": 980
    },
    {
        "id": "syntax_typer",
        "title": "Syntax Speed Typer Sprint",
        "category": "Code & Dev Logic",
        "icon": "bi-keyboard",
        "color": "info",
        "desc": "Type programming keywords, lambda syntax, and function definitions against a 30s countdown.",
        "difficulty": "Easy",
        "plays": 2150
    },
    {
        "id": "code_output",
        "title": "Code Output Predictor",
        "category": "Code & Dev Logic",
        "icon": "bi-code-slash",
        "color": "warning",
        "desc": "Predict tricky Python and JavaScript snippet prints under 15 seconds.",
        "difficulty": "Medium",
        "plays": 1640
    },
    {
        "id": "regex_puzzle",
        "title": "Regex Pattern Matcher",
        "category": "Code & Dev Logic",
        "icon": "bi-regex",
        "color": "danger",
        "desc": "Identify matching regular expressions for emails, dates, IP addresses, and hex colors.",
        "difficulty": "Hard",
        "plays": 870
    },
    {
        "id": "bug_hunter",
        "title": "Bug Hunter Zap",
        "category": "Code & Dev Logic",
        "icon": "bi-bug",
        "color": "danger",
        "desc": "Spot the syntax bug or off-by-one index error in 4 lines of code before time runs out.",
        "difficulty": "Medium",
        "plays": 1320
    },
    {
        "id": "stack_balancer",
        "title": "Bracket Stack Balancer",
        "category": "Code & Dev Logic",
        "icon": "bi-layers",
        "color": "primary",
        "desc": "Push and pop brackets to determine if complex expressions like {[()]} are mathematically valid.",
        "difficulty": "Medium",
        "plays": 1110
    },
    {
        "id": "git_blitz",
        "title": "Git Command Blitz",
        "category": "Code & Dev Logic",
        "icon": "bi-git",
        "color": "dark",
        "desc": "Rapidly match engineering scenarios to Git commands: rebase, cherry-pick, stash, checkout, merge.",
        "difficulty": "Easy",
        "plays": 1780
    },

    # Category 2: Math & Quant Aptitude (7 Games)
    {
        "id": "mental_math_sprint",
        "title": "Mental Math 60-Second Sprint",
        "category": "Math & Quant Aptitude",
        "icon": "bi-calculator",
        "color": "success",
        "desc": "Solve lightning addition, multiplication, division, and subtraction combos to beat the clock.",
        "difficulty": "Easy",
        "plays": 3410
    },
    {
        "id": "number_series",
        "title": "Number Series Detective",
        "category": "Math & Quant Aptitude",
        "icon": "bi-sort-numeric-up",
        "color": "warning",
        "desc": "Find the missing number in arithmetic, geometric, square difference, and Fibonacci sequences.",
        "difficulty": "Medium",
        "plays": 2240
    },
    {
        "id": "prime_blitz",
        "title": "Prime Number Blitz",
        "category": "Math & Quant Aptitude",
        "icon": "bi-lightning",
        "color": "primary",
        "desc": "Fast reaction challenge: tap whether the incoming number is Prime or Composite in 3 seconds.",
        "difficulty": "Easy",
        "plays": 1890
    },
    {
        "id": "percentage_hustle",
        "title": "Percentage & Discount Hustle",
        "category": "Math & Quant Aptitude",
        "icon": "bi-percent",
        "color": "info",
        "desc": "Calculate swift mental discounts, markups, and profit margins for corporate and aptitude questions.",
        "difficulty": "Medium",
        "plays": 1450
    },
    {
        "id": "probability_dice",
        "title": "Probability Odds Predictor",
        "category": "Math & Quant Aptitude",
        "icon": "bi-dice-5",
        "color": "secondary",
        "desc": "Calculate theoretical odds and fractions on rolling dice sums, coin tosses, and card draws.",
        "difficulty": "Medium",
        "plays": 980
    },
    {
        "id": "speed_algebra",
        "title": "Speed Algebra Equation Solver",
        "category": "Math & Quant Aptitude",
        "icon": "bi-x-diamond",
        "color": "danger",
        "desc": "Quickly isolate and solve for variable X in linear equations against an accelerating timer.",
        "difficulty": "Medium",
        "plays": 1130
    },
    {
        "id": "time_and_work",
        "title": "Time & Work Rapid Estimator",
        "category": "Math & Quant Aptitude",
        "icon": "bi-stopwatch",
        "color": "success",
        "desc": "Calculate combined work completion days for collaborative teams and pipe flow rates.",
        "difficulty": "Hard",
        "plays": 890
    },

    # Category 3: Brain Teasers & CS Logic (6 Games)
    {
        "id": "logic_gates",
        "title": "Logic Gates Circuit Sandbox",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-cpu",
        "color": "primary",
        "desc": "Wire AND, OR, NOT, and XOR inputs together to illuminate the green output circuit lightbulb.",
        "difficulty": "Medium",
        "plays": 2420
    },
    {
        "id": "bytes_2048",
        "title": "2048 Byte Edition",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-grid-3x3",
        "color": "warning",
        "desc": "Slide and merge powers of 2 (2 Bytes, 4B, 8B, 16B, ..., 2048MB) on a 4x4 matrix.",
        "difficulty": "Medium",
        "plays": 3980
    },
    {
        "id": "memory_matrix",
        "title": "Data Structures Memory Match",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-diagram-3",
        "color": "success",
        "desc": "Flip memory cards to match data structure names (Array, BST, Hash Table) to their lookup speeds.",
        "difficulty": "Easy",
        "plays": 1670
    },
    {
        "id": "tower_of_hanoi",
        "title": "Tower of Hanoi 3-Disk Challenge",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-bar-chart-steps",
        "color": "info",
        "desc": "Move all 3 disks from Peg A to Peg C in optimal 7 moves without placing a larger disk on a smaller one.",
        "difficulty": "Medium",
        "plays": 1290
    },
    {
        "id": "keyword_scramble",
        "title": "Tech Keyword Anagram Scramble",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-fonts",
        "color": "danger",
        "desc": "Unscramble jumbled letters into real tech terms: PYTHON, RECURSION, POLYMORPHISM, DATABASE.",
        "difficulty": "Easy",
        "plays": 2100
    },
    {
        "id": "base_converter",
        "title": "Binary & Hex Decryptor",
        "category": "Brain Teasers & CS Logic",
        "icon": "bi-shield-lock",
        "color": "dark",
        "desc": "Translate 4-bit binary nibbles (1011) or Hex characters (0x0F) into decimal numbers instantly.",
        "difficulty": "Medium",
        "plays": 1410
    }
]

@games_bp.route('/')
@login_required
def index():
    category_filter = request.args.get('category', 'all')
    search = request.args.get('q', '').strip().lower()

    filtered = GAMES_CATALOG
    if category_filter != 'all':
        filtered = [g for g in filtered if g['category'] == category_filter]

    if search:
        filtered = [g for g in filtered if search in g['title'].lower() or search in g['desc'].lower()]

    categories = ["Code & Dev Logic", "Math & Quant Aptitude", "Brain Teasers & CS Logic"]

    return render_template(
        'games/index.html',
        games=filtered,
        total_games=len(GAMES_CATALOG),
        category_filter=category_filter,
        search=search,
        categories=categories
    )

@games_bp.route('/log-score', methods=['POST'])
@login_required
def log_score():
    """Optional endpoint to log game completion activity for streaks and heatmap."""
    data = request.get_json() or {}
    game_title = data.get('game_title', 'Brain Refresh Game')
    score = data.get('score', 10)

    if current_user.is_student() and current_user.student_profile:
        log_activity(
            student_id=current_user.student_profile.id,
            activity_type='games',
            activity_title=f"Played {game_title} (Score: {score})",
            duration_minutes=10
        )
        return jsonify({"status": "success", "message": "Activity recorded!"})
    return jsonify({"status": "ok"})
