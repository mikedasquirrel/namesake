"""
Common American Names Dataset

Top 1,000 most common American names for baseline comparison.
From US Census data + common combinations.
"""

# Top 500 first names (male/female combined, by frequency)
COMMON_FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda",
    "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Lisa", "Daniel", "Nancy",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Andrew", "Emily", "Paul", "Donna", "Joshua", "Michelle",
    "Kenneth", "Carol", "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Amy", "Gary", "Kathleen",
    "Nicholas", "Angela", "Eric", "Shirley", "Jonathan", "Anna", "Stephen", "Brenda",
    "Larry", "Pamela", "Justin", "Emma", "Scott", "Nicole", "Brandon", "Helen",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Carolyn", "Patrick", "Janet", "Jack", "Catherine",
    "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane", "Aaron", "Ruth",
    "Jose", "Julie", "Adam", "Olivia", "Nathan", "Joyce", "Henry", "Virginia",
    "Douglas", "Victoria", "Zachary", "Kelly", "Peter", "Lauren", "Kyle", "Christina",
    "Noah", "Joan", "Ethan", "Evelyn", "Jeremy", "Judith", "Christian", "Megan",
    "Walter", "Andrea", "Keith", "Cheryl", "Roger", "Hannah", "Terry", "Jacqueline",
    "Austin", "Martha", "Sean", "Madison", "Gerald", "Teresa", "Carl", "Gloria",
    "Dylan", "Sara", "Harold", "Janice", "Jordan", "Jean", "Jesse", "Abigail",
    "Bryan", "Kathryn", "Lawrence", "Ann", "Arthur", "Sophia", "Gabriel", "Frances",
    "Bruce", "Judy", "Logan", "Alice", "Albert", "Isabella", "Willie", "Julia",
    "Joe", "Grace", "Billy", "Denise", "Alan", "Amber", "Juan", "Doris",
]

# Top 200 surnames (by frequency)
COMMON_SURNAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell",
    "Sullivan", "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher",
    "Vasquez", "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant",
    "Herrera", "Gibson", "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray",
    "Ford", "Castro", "Marshall", "Owens", "Harrison", "Fernandez", "McDonald", "Woods",
    "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb",
    "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
    "Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Munoz",
    "Hunt", "Hicks", "Holmes", "Palmer", "Wagner", "Black", "Robertson", "Boyd",
    "Rose", "Stone", "Salazar", "Fox", "Warren", "Mills", "Meyer", "Rice",
]

def generate_population_names(n=5000):
    """Generate n realistic American names"""
    import random
    
    names = []
    
    # Generate combinations
    for i in range(n):
        first = random.choice(COMMON_FIRST_NAMES)
        last = random.choice(COMMON_SURNAMES)
        
        # Sometimes add middle name or suffix
        if random.random() < 0.3:
            middle = random.choice(COMMON_FIRST_NAMES)
            name = f"{first} {middle} {last}"
        else:
            name = f"{first} {last}"
        
        # Sometimes add Jr/Sr
        if random.random() < 0.05:
            name += " Jr"
        
        names.append(name)
    
    return names

if __name__ == '__main__':
    names = generate_population_names(5000)
    print(f"Generated {len(names)} realistic American names")
    print("\nSample:")
    for name in names[:10]:
        print(f"  {name}")

