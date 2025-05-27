import sqlite3
import bcrypt

def insert_test_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Insert sample users (unchanged)
    users = [('student1@edu.com', 'John Smith', 'Masters in Engineering', '1995-05-15', bcrypt.hashpw('find_me'.encode('utf-8'), bcrypt.gensalt()), 'user'),
            ('student2@edu.com', 'Emma Wilson', 'Bachelor in Computer Science', '1998-08-22', bcrypt.hashpw('find_me'.encode('utf-8'), bcrypt.gensalt()), 'user'),
            ('student3@edu.com', 'Michael Brown', 'PhD in Physics', '1993-11-30', bcrypt.hashpw('find_me'.encode('utf-8'), bcrypt.gensalt()), 'user')]
    cursor.executemany("INSERT OR IGNORE INTO users (username, full_name, qualification, dob, password, role) VALUES (?, ?, ?, ?, ?, ?)", users)

    # Insert subjects (unchanged)
    subjects = [('Physics', 'Study of matter and energy', None),
               ('Chemistry', 'Study of elements and compounds', None),
               ('Biology', 'Study of living organisms', None),
               ('Mathematics', 'Study of numbers and logic', None),
               ('Computer Science', 'Study of computation', None)]
    cursor.executemany("INSERT INTO subjects (name, description, additional_fields) VALUES (?, ?, ?)", subjects)

    # Insert chapters (unchanged)
    chapters = [(1, 'Mechanics', 'Motion and forces', None),
               (1, 'Thermodynamics', 'Heat and energy', None),
               (1, 'Electromagnetism', 'Electricity and magnetism', None),
               (2, 'Organic Chemistry', 'Carbon compounds', None),
               (2, 'Inorganic Chemistry', 'Metals and minerals', None),
               (2, 'Physical Chemistry', 'Chemical principles', None),
               (3, 'Genetics', 'Heredity and variation', None),
               (3, 'Ecology', 'Ecosystems', None),
               (3, 'Microbiology', 'Microorganisms', None),
               (4, 'Algebra', 'Equations and variables', None),
               (4, 'Calculus', 'Rates of change', None),
               (4, 'Geometry', 'Shapes and spaces', None),
               (5, 'Programming', 'Coding fundamentals', None),
               (5, 'Algorithms', 'Problem-solving methods', None),
               (5, 'Databases', 'Data storage', None)]
    cursor.executemany("INSERT INTO chapters (subject_id, name, description, additional_fields) VALUES (?, ?, ?, ?)", chapters)

    # Insert quizzes with 5-minute duration
    quizzes = [(1, 'Mechanics Quiz 1', '2025-05-01', 5, 'Basic mechanics'),
              (1, 'Mechanics Quiz 2', '2025-05-08', 5, 'Advanced mechanics'),
              (2, 'Thermodynamics Quiz 1', '2025-05-15', 5, 'Laws of thermodynamics'),
              (2, 'Thermodynamics Quiz 2', '2025-05-22', 5, 'Heat transfer'),
              (3, 'Electromagnetism Quiz 1', '2025-05-29', 5, 'Electric fields'),
              (3, 'Electromagnetism Quiz 2', '2025-06-05', 5, 'Magnetic fields'),
              (4, 'Organic Quiz 1', '2025-06-12', 5, 'Hydrocarbons'),
              (4, 'Organic Quiz 2', '2025-06-19', 5, 'Functional groups'),
              (5, 'Inorganic Quiz 1', '2025-06-26', 5, 'Periodic table'),
              (5, 'Inorganic Quiz 2', '2025-07-03', 5, 'Chemical bonds'),
              (6, 'Physical Quiz 1', '2025-07-10', 5, 'Reaction kinetics'),
              (6, 'Physical Quiz 2', '2025-07-17', 5, 'Thermochemistry'),
              (7, 'Genetics Quiz 1', '2025-07-24', 5, 'Mendelian inheritance'),
              (7, 'Genetics Quiz 2', '2025-07-31', 5, 'DNA structure'),
              (8, 'Ecology Quiz 1', '2025-08-07', 5, 'Food chains'),
              (8, 'Ecology Quiz 2', '2025-08-14', 5, 'Biomes'),
              (9, 'Microbiology Quiz 1', '2025-08-21', 5, 'Bacteria'),
              (9, 'Microbiology Quiz 2', '2025-08-28', 5, 'Viruses'),
              (10, 'Algebra Quiz 1', '2025-09-04', 5, 'Linear equations'),
              (10, 'Algebra Quiz 2', '2025-09-11', 5, 'Polynomials'),
              (11, 'Calculus Quiz 1', '2025-09-18', 5, 'Derivatives'),
              (11, 'Calculus Quiz 2', '2025-09-25', 5, 'Integrals'),
              (12, 'Geometry Quiz 1', '2025-10-02', 5, 'Triangles'),
              (12, 'Geometry Quiz 2', '2025-10-09', 5, 'Circles'),
              (13, 'Programming Quiz 1', '2025-10-16', 5, 'Variables'),
              (13, 'Programming Quiz 2', '2025-10-23', 5, 'Loops'),
              (14, 'Algorithms Quiz 1', '2025-10-30', 5, 'Sorting'),
              (14, 'Algorithms Quiz 2', '2025-11-06', 5, 'Searching'),
              (15, 'Databases Quiz 1', '2025-11-13', 5, 'SQL Basics'),
              (15, 'Databases Quiz 2', '2025-11-20', 5, 'Normalization')]
    cursor.executemany("INSERT INTO quizzes (chapter_id, quiz_name, date_of_quiz, time_duration, remarks) VALUES (?, ?, ?, ?, ?)", quizzes)

    # 150 Validated Questions (5 per quiz)
    questions = [
        # Physics - Mechanics (Quiz 1-2)
        (1, "What is Newton's First Law called?", "Law of Inertia", "Law of Momentum", "Law of Acceleration", "Law of Gravity", 1),
        (1, "What quantity is mass × velocity?", "Momentum", "Force", "Energy", "Power", 1),
        (1, "Unit of force in SI system?", "Newton", "Joule", "Watt", "Pascal", 1),
        (1, "Acceleration due to gravity (m/s²)?", "9.8", "8.9", "10.2", "6.7", 1),
        (1, "Rate of change of velocity?", "Acceleration", "Speed", "Momentum", "Force", 1),

        (2, "Conserved in elastic collisions?", "Momentum & KE", "Only Momentum", "Only KE", "Neither", 1),
        (2, "Rotational analog of mass?", "Moment of Inertia", "Torque", "Angular Momentum", "Centripetal Force", 1),
        (2, "Work done against gravity depends on?", "Height", "Mass", "Both", "Neither", 3),
        (2, "Unit of angular momentum?", "kg·m²/s", "N·m", "J·s", "W/s²", 1),
        (2, "Hooke's Law relates to:", "Springs", "Gases", "Fluids", "Electrons", 1),

        # Physics - Thermodynamics (Quiz 3-4)
        (3, "First law relates to:", "Energy Conservation", "Entropy", "Heat Engines", "Absolute Zero", 1),
        (3, "Absolute zero in Kelvin?", "0", "273", "-273", "100", 1),
        (3, "Adiabatic process characteristic?", "No heat transfer", "Constant pressure", "Constant volume", "Isothermal", 1),
        (3, "Carnot efficiency depends on:", "Temp difference", "Working substance", "Pressure", "Volume", 1),
        (3, "Unit of specific heat capacity?", "J/(kg·K)", "W/m²", "N·m", "Pa·s", 1),

        (4, "Heat transfer through EM waves?", "Radiation", "Conduction", "Convection", "Diffusion", 1),
        (4, "Fourier's Law relates to:", "Heat conduction", "Radiation", "Convection", "Phase Change", 1),
        (4, "Black body radiation concept by?", "Planck", "Einstein", "Newton", "Bohr", 1),
        (4, "Stefan-Boltzmann Law relates:", "Radiated Energy", "Heat Transfer", "Pressure", "Entropy", 1),
        (4, "Thermal conductivity unit?", "W/(m·K)", "J/K", "N/m²", "m²/s", 1),

        # Physics - Electromagnetism (Quiz 5-6)
        (5, "Coulomb's Law describes:", "Electric Force", "Magnetic Force", "Gravity", "Nuclear Force", 1),
        (5, "Electric field unit?", "N/C", "V/m", "Both", "Neither", 3),
        (5, "Charge on electron?", "-1.6e-19 C", "+1.6e-19 C", "Neutral", "Variable", 1),
        (5, "Gauss's Law relates:", "Electric Flux", "Magnetic Flux", "Current", "Resistance", 1),
        (5, "Superconductor property?", "Zero Resistance", "High Resistance", "Magnetic", "Insulating", 1),

        (6, "Right-Hand Rule applies to:", "Magnetic Force", "Electric Force", "Gravity", "Friction", 1),
        (6, "Faraday's Law concerns:", "EM Induction", "Electrostatics", "Current", "Resistance", 1),
        (6, "Transformer works via:", "Mutual Induction", "Self Induction", "Conduction", "Radiation", 1),
        (6, "Lenz's Law relates to:", "Induced Current", "Magnetic Poles", "Charge", "Resistance", 1),
        (6, "Unit of magnetic flux?", "Weber", "Tesla", "Henry", "Farad", 1),

        # Chemistry - Organic (Quiz 7-8)
        (7, "Alkanes general formula?", "CₙH₂ₙ₊₂", "CₙH₂ₙ", "CₙH₂ₙ₋₂", "CₙHₙ", 1),
        (7, "Alcohol functional group?", "-OH", "-COOH", "-CHO", "-NH₂", 1),
        (7, "Tetrahedral geometry in?", "Methane", "Ethene", "Benzene", "Ammonia", 1),
        (7, "Isomerism with same formula?", "Structural", "Geometric", "Optical", "All", 4),
        (7, "Number of σ bonds in ethyne?", "3", "2", "1", "4", 1),

        (8, "Ketone functional group?", "C=O", "-COOH", "-OH", "-NH₂", 1),
        (8, "Geometric isomerism requires?", "Double bond", "Single bond", "Triple bond", "Ring", 1),
        (8, "Benedict's reagent tests for?", "Aldehydes", "Ketones", "Alcohols", "Esters", 1),
        (8, "Esterification reaction type?", "Condensation", "Addition", "Substitution", "Oxidation", 1),
        (8, "IUPAC name for CH₃CH₂OH?", "Ethanol", "Methanol", "Propanol", "Butanol", 1),

        # Chemistry - Inorganic (Quiz 9-10)
        (9, "Noble gases are in group?", "18", "1", "2", "17", 1),
        (9, "Most electronegative element?", "Fluorine", "Oxygen", "Chlorine", "Nitrogen", 1),
        (9, "Alkali metals in group?", "1", "2", "17", "18", 1),
        (9, "Ionic bond forms between?", "Metal & Non-metal", "Non-metals", "Metals", "Noble gases", 1),
        (9, "Oxidation state of O in H₂O?", "-2", "-1", "+1", "+2", 1),

        (10, "Coordination number in NaCl?", "6", "4", "8", "12", 1),
        (10, "Alloy of Hg with metals?", "Amalgam", "Steel", "Bronze", "Brass", 1),
        (10, "Hardest natural substance?", "Diamond", "Graphite", "Quartz", "Topaz", 1),
        (10, "pH of strong acid?", "<7", "7", ">7", "14", 1),
        (10, "Common oxidation state of Na?", "+1", "+2", "-1", "-2", 1),

        # Chemistry - Physical (Quiz 11-12)
        (11, "Ideal Gas Law?", "PV=nRT", "E=mc²", "F=ma", "V=IR", 1),
        (11, "Unit of rate constant (1st order)?", "s⁻¹", "mol/L", "L/mol·s", "mol²/L²·s", 1),
        (11, "Le Chatelier's Principle concerns?", "Equilibrium", "Kinetics", "Thermodynamics", "Structure", 1),
        (11, "Enthalpy change unit?", "kJ/mol", "J/K", "W/s", "Pa·m³", 1),
        (11, "Catalyst effect on equilibrium?", "None", "Shifts left", "Shifts right", "Changes K", 1),

        (12, "Hess's Law relates to:", "Enthalpy", "Entropy", "Rate", "Equilibrium", 1),
        (12, "Entropy measure of?", "Disorder", "Energy", "Order", "Heat", 1),
        (12, "ΔG < 0 indicates:", "Spontaneous", "Non-spontaneous", "Equilibrium", "No reaction", 1),
        (12, "Arrhenius equation relates:", "Rate & Temp", "Pressure & Vol", "KE & Temp", "pH & Conc", 1),
        (12, "Oxidation involves:", "Loss of e⁻", "Gain of e⁻", "No e⁻ change", "Proton gain", 1),

        # Biology - Genetics (Quiz 13-14)
        (13, "Mendel studied:", "Pea plants", "Fruit flies", "Bacteria", "Mice", 1),
        (13, "Genotype for homozygous?", "AA", "Aa", "aa", "AB", 1),
        (13, "Human diploid number?", "46", "23", "48", "24", 1),
        (13, "DNA structure discovered by?", "Watson & Crick", "Mendel", "Darwin", "Einstein", 1),
        (13, "RNA contains:", "Ribose", "Deoxyribose", "Glucose", "Fructose", 1),

        (14, "DNA replication is:", "Semi-conservative", "Conservative", "Dispersive", "Random", 1),
        (14, "Transcription produces:", "mRNA", "Protein", "tRNA", "rRNA", 1),
        (14, "Genetic code is:", "Universal", "Organism-specific", "Tissue-specific", "Variable", 1),
        (14, "Mutation in gametes affects:", "Offspring", "Individual", "Neither", "Both", 1),
        (14, "PCR amplifies:", "DNA", "RNA", "Protein", "Lipids", 1),

        # Biology - Ecology (Quiz 15-16)
        (15, "Primary producers are:", "Plants", "Herbivores", "Carnivores", "Decomposers", 1),
        (15, "Nitrogen-fixing bacteria live in:", "Root nodules", "Leaves", "Soil", "Water", 1),
        (15, "Energy flow is:", "Unidirectional", "Cyclic", "Bidirectional", "Random", 1),
        (15, "Ozone layer protects from:", "UV", "IR", "Visible light", "Radio waves", 1),
        (15, "Greenhouse gas example?", "CO₂", "O₂", "N₂", "H₂O", 1),

        (16, "Largest biome on Earth?", "Marine", "Forest", "Desert", "Tundra", 1),
        (16, "Symbiosis where both benefit?", "Mutualism", "Parasitism", "Commensalism", "Predation", 1),
        (16, "Keystone species example?", "Sea otter", "Deer", "Grass", "Mushroom", 1),
        (16, "Primary succession occurs on:", "Bare rock", "Disturbed soil", "Burnt forest", "Abandoned field", 1),
        (16, "Carrying capacity is:", "Max population", "Growth rate", "Death rate", "Birth rate", 1),

        # Biology - Microbiology (Quiz 17-18)
        (17, "Prokaryotic cells lack:", "Nucleus", "Cell wall", "Ribosomes", "DNA", 1),
        (17, "Binary fission is:", "Asexual reproduction", "Sexual", "Meiosis", "Fertilization", 1),
        (17, "Antibiotics target:", "Bacteria", "Viruses", "Fungi", "All", 1),
        (17, "Gram-positive bacteria have:", "Thick cell wall", "Thin cell wall", "No wall", "Cellulose", 1),
        (17, "Autotrophic bacteria use:", "CO₂", "Organic matter", "Oxygen", "Nitrogen", 1),

        (18, "Viruses contain:", "DNA/RNA", "Cytoplasm", "Ribosomes", "Mitochondria", 1),
        (18, "HIV attacks:", "T-cells", "B-cells", "Platelets", "Neurons", 1),
        (18, "Vaccines work by:", "Stimulating immunity", "Killing pathogens", "Blocking receptors", "All", 1),
        (18, "Prions cause:", "Mad cow disease", "Flu", "Tuberculosis", "Malaria", 1),
        (18, "Lytic cycle results in:", "Host cell death", "Latency", "Symbiosis", "Immunity", 1),

        # Math - Algebra (Quiz 19-20)
        (19, "Solve 2x + 3 = 7", "2", "3", "4", "5", 1),
        (19, "Quadratic formula?", "(-b ± √(b²-4ac))/2a", "b²-4ac", "ax²+bx+c=0", "y=mx+c", 1),
        (19, "Factor x² - 4", "(x+2)(x-2)", "(x-2)²", "(x+4)(x-4)", "Prime", 1),
        (19, "Slope of y=3x+2?", "3", "2", "0", "Undefined", 1),
        (19, "System with no solution?", "Inconsistent", "Consistent", "Dependent", "Independent", 1),

        (20, "Degree of x³ + 2x + 1?", "3", "2", "1", "0", 1),
        (20, "Sum of roots of 2x² -5x +3=0?", "5/2", "3/2", "-5/2", "-3/2", 1),
        (20, "Complex number i² = ?", "-1", "1", "0", "Undefined", 1),
        (20, "Arithmetic sequence difference?", "Common difference", "Common ratio", "Variable", "Zero", 1),
        (20, "Matrix with determinant 0?", "Singular", "Non-singular", "Identity", "Diagonal", 1),

        # Math - Calculus (Quiz 21-22)
        (21, "Derivative of x²?", "2x", "x", "2", "0", 1),
        (21, "∫2x dx = ?", "x² + C", "2x² + C", "x + C", "2 + C", 1),
        (21, "L'Hôpital's Rule applies to:", "0/0 form", "∞/∞", "Both", "Neither", 3),
        (21, "Second derivative gives:", "Acceleration", "Velocity", "Position", "Displacement", 1),
        (21, "Critical points occur when:", "f'(x)=0", "f(x)=0", "f''(x)=0", "f(x) max", 1),

        (22, "∫₀¹ x dx = ?", "0.5", "1", "0", "2", 1),
        (22, "Chain rule: d/dx[f(g(x))] = ?", "f'(g(x))·g'(x)", "f(g'(x))", "f'(x)·g(x)", "f(g(x))·g'(x)", 1),
        (22, "Partial derivatives used in:", "Multivariable calc", "Integral calc", "Series", "Differential eq", 1),
        (22, "Area between curves uses:", "Integration", "Differentiation", "Limits", "Series", 1),
        (22, "Derivative of ln(x)?", "1/x", "e^x", "ln(x)", "0", 1),

        # Math - Geometry (Quiz 23-24)
        (23, "Triangle angles sum to?", "180°", "90°", "360°", "270°", 1),
        (23, "Pythagorean theorem?", "a²+b²=c²", "E=mc²", "F=ma", "V=IR", 1),
        (23, "Area of circle?", "πr²", "2πr", "πd", "4/3πr³", 1),
        (23, "Regular hexagon angles?", "120°", "90°", "60°", "180°", 1),
        (23, "Volume of sphere?", "4/3πr³", "πr²h", "1/3πr²h", "2πr²", 1),

        (24, "Congruent triangles have:", "Same shape & size", "Same shape", "Same size", "Different angles", 1),
        (24, "Parallelogram area formula?", "base × height", "½bh", "πr²", "a + b + c", 1),
        (24, "Number of diagonals in pentagon?", "5", "6", "7", "10", 1),
        (24, "Similar triangles have:", "Equal angles", "Equal sides", "Both", "Neither", 1),
        (24, "Slope of vertical line?", "Undefined", "0", "1", "-1", 1),

        # CS - Programming (Quiz 25-26)
        (25, "Python is:", "Interpreted", "Compiled", "Assembly", "Machine code", 1),
        (25, "String 'Hello' length?", "5", "6", "4", "7", 1),
        (25, "Loop for fixed iterations?", "for", "while", "do-while", "if", 1),
        (25, "Index of first list element?", "0", "1", "-1", "None", 1),
        (25, "Function to output text?", "print()", "input()", "return", "def", 1),

        (26, "Which is a OOP concept?", "Inheritance", "Looping", "Variable", "Operator", 1),
        (26, "Exception handling uses:", "try-except", "if-else", "for", "while", 1),
        (26, "Recursion is:", "Self-calling", "Looping", "Branching", "Parallel", 1),
        (26, "Global variable declared with:", "global", "local", "var", "const", 1),
        (26, "Which is mutable?", "List", "Tuple", "String", "None", 1),

        # CS - Algorithms (Quiz 27-28)
        (27, "O(1) time complexity example?", "Array access", "Linear search", "Bubble sort", "Binary search", 1),
        (27, "Bubble sort complexity?", "O(n²)", "O(n)", "O(n log n)", "O(1)", 1),
        (27, "Divide & conquer example?", "Merge sort", "Bubble sort", "Linear search", "Insertion sort", 1),
        (27, "DFS uses:", "Stack", "Queue", "Heap", "Array", 1),
        (27, "Hash table average search?", "O(1)", "O(n)", "O(log n)", "O(n²)", 1),

        (28, "Dynamic programming uses:", "Memoization", "Sorting", "Searching", "Hashing", 1),
        (28, "Greedy algorithm makes:", "Local optimal", "Global optimal", "Random", "No choices", 1),
        (28, "Binary search requires:", "Sorted data", "Unsorted", "Hashed", "Encrypted", 1),
        (28, "Worst case for quicksort?", "O(n²)", "O(n log n)", "O(n)", "O(1)", 1),
        (28, "BFS uses:", "Queue", "Stack", "Heap", "Tree", 1),

        # CS - Databases (Quiz 29-30)
        (29, "SQL stands for:", "Structured Query Language", "Simple Query", "System Query", "Standard Query", 1),
        (29, "Primary key characteristic?", "Unique", "Nullable", "Duplicate", "Optional", 1),
        (29, "SELECT * FROM table;", "All columns", "First column", "Last column", "No columns", 1),
        (29, "ACID property?", "Atomicity", "Availability", "Speed", "Capacity", 1),
        (29, "JOIN combines:", "Tables", "Databases", "Servers", "Files", 1),

        (30, "Normalization reduces:", "Redundancy", "Security", "Speed", "Size", 1),
        (30, "1NF requires:", "Atomic values", "No keys", "Duplicates", "Joins", 1),
        (30, "NoSQL example?", "MongoDB", "MySQL", "Oracle", "SQLite", 1),
        (30, "Index improves:", "Search speed", "Data security", "Backup", "Storage", 1),
        (30, "DELETE vs TRUNCATE?", "TRUNCATE faster", "DELETE faster", "Same", "None", 1)
    ]

    cursor.executemany("INSERT INTO questions (quiz_id, question_statement, option1, option2, option3, option4, correct_option) VALUES (?, ?, ?, ?, ?, ?, ?)", questions)

    conn.commit()
    conn.close()

insert_test_data()