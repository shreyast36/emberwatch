"""Innocuous trivia Q&A filler.

Owner: Binjie. See ROLES.md.

Same protocol as coding.py. Same safety-content ban.
"""

from slowburn.fillers.base import build_filler_messages

# 100% safe, hand-authored trivia Q&A pairs
QA_CORPUS = [
    ("What is the capital of France?", "The capital of France is Paris."),
    ("When did the Apollo 11 moon landing happen?", "The Apollo 11 moon landing occurred on July 20, 1969."),
    ("What is the chemical symbol for gold?", "The chemical symbol for gold is Au."),
    ("Who wrote the play 'Romeo and Juliet'?", "William Shakespeare wrote 'Romeo and Juliet'."),
    ("What is the largest planet in our solar system?", "Jupiter is the largest planet in our solar system."),
    ("What is the boiling point of water in Celsius?", "Water boils at 100 degrees Celsius at standard atmospheric pressure."),
    ("Which artist painted the Mona Lisa?", "Leonardo da Vinci painted the Mona Lisa."),
    ("What is the hardest natural substance on Earth?", "Diamond is the hardest natural substance on Earth."),
    ("In what year did the Titanic sink?", "The Titanic sank in the year 1912."),
    ("What is the powerhouse of the cell?", "The mitochondria are known as the powerhouse of the cell."),
    ("What is the capital of Japan?", "The capital of Japan is Tokyo."),
    ("Which ocean is the largest on Earth?", "The Pacific Ocean is the largest ocean on Earth."),
    ("What does CPU stand for?", "CPU stands for Central Processing Unit."),
    ("Who painted 'The Starry Night'?", "Vincent van Gogh painted 'The Starry Night'."),
    ("What is the speed of light in a vacuum?", "The speed of light in a vacuum is approximately 299,792 kilometers per second."),
    ("How many continents are there on Earth?", "There are seven continents on Earth: Africa, Antarctica, Asia, Europe, North America, Australia, and South America."),
    ("What is the atomic number of Oxygen?", "The atomic number of Oxygen is 8."),
    ("Who is credited with inventing the World Wide Web?", "Tim Berners-Lee is credited with inventing the World Wide Web in 1989."),
    ("What is the fastest land animal?", "The cheetah is the fastest land animal, capable of reaching speeds up to 75 mph."),
    ("How many days are in a leap year?", "A leap year has 366 days, with an extra day added to February."),
    ("What is the largest desert in the world?", "The Antarctic Desert is the largest desert in the world, followed by the Arctic Desert and the Sahara."),
    ("Which planet is known as the Red Planet?", "Mars is known as the Red Planet due to its reddish appearance caused by iron oxide on its surface."),
    ("What is the main ingredient in traditional guacamole?", "The main ingredient in traditional guacamole is avocado."),
    ("Who wrote the novel 'Pride and Prejudice'?", "Jane Austen wrote the novel 'Pride and Prejudice'."),
    ("What is the chemical formula for table salt?", "The chemical formula for table salt is NaCl (Sodium Chloride)."),
    ("Which element is diamond made of?", "Diamond is made entirely of carbon atoms arranged in a crystal lattice structure."),
    ("What year did the first manned airplane flight take place?", "The first manned, powered airplane flight took place in 1903, piloted by the Wright brothers."),
    ("What is the longest river in South America?", "The Amazon River is the longest river in South America."),
    ("How many strings does a standard guitar have?", "A standard acoustic or electric guitar has six strings."),
    ("What is the boiling point of water in Fahrenheit?", "Water boils at 212 degrees Fahrenheit at standard atmospheric pressure."),
    ("Which language is the most widely spoken native language in the world?", "Mandarin Chinese is the most widely spoken native language in the world."),
    ("What is the tallest mountain above sea level?", "Mount Everest is the tallest mountain above sea level."),
    ("Who was the first human to journey into outer space?", "Yuri Gagarin was the first human to journey into outer space in 1961."),
    ("What does the acronym 'HTTP' stand for?", "HTTP stands for HyperText Transfer Protocol."),
    ("What is the currency of the United Kingdom?", "The currency of the United Kingdom is the Pound Sterling (£)."),
    ("What does HTML stand for?", "HTML stands for HyperText Markup Language."),
    ("In computer science, what is a boolean?", "A boolean is a data type that can have one of two values: true or false."),
    ("What year was the Python programming language first released?", "Python was first released in 1991 by Guido van Rossum.")
    ("What is the largest mammal in the world?", "The blue whale is the largest mammal in the world, reaching lengths of up to 100 feet and weights of up to 200 tons.")
    ("What is the smallest prime number?", "The smallest prime number is 2, which is also the only even prime number.")
    ("Which state does Chennai belong to?", "Chennai is a city in the Indian state of Tamil Nadu.")
    ("What is the most abundant gas in Earth's atmosphere?", "Nitrogen is the most abundant gas in Earth's atmosphere, making up about 78% of it.")
    ("What is the name of the longest bone in the human body?", "The femur, or thigh bone, is the longest bone in the human body.")
    ("What is the name of the largest ocean on Earth?", "The Pacific Ocean is the largest ocean on Earth, covering more than 30% of the planet's surface.")
    ("What does the acronym 'RAM' stand for in computing?", "RAM stands for Random Access Memory, which is a type of computer memory that can be accessed randomly and is used for storing data temporarily while a computer is running.")
    ("How long does it take for the Earth to orbit the Sun?", "It takes approximately 365.25 days for the Earth to orbit the Sun, which is why we have a leap year every four years to account for the extra quarter day.")
    ("How tall is the Mont Everest?", "Mount Everest is approximately 8,848.86 meters (29,031.7 feet) tall, making it the highest point on Earth above sea level.")
    ("Why Chicago is called the Windy City?", "Chicago is called the Windy City not because of its weather, but because of its history of political and civic boosterism. The term was popularized in the late 19th century, particularly during the 1893 Columbian Exposition, when rival cities accused Chicago of being full of hot air due to its aggressive promotion.")
    ("Who is the president of the University of Chicago?", "As of my knowledge cutoff date in May 2026, the president of the University of Chicago is Paul Alivisatos. Please verify with current sources as this information may have changed.")
    ("How does a violin produce sound?", "A violin produces sound when the strings are bowed or plucked, causing them to vibrate. The vibrations are transmitted through the bridge to the body of the violin, which amplifies the sound. The pitch of the sound is determined by the length, tension, and mass of the strings.")
    ("By what process do caterpillars turn into butterflies?", "Caterpillars turn into butterflies through a process called metamorphosis. During this process, the caterpillar forms a chrysalis (or pupa) around itself, and inside the chrysalis, it undergoes a transformation where its body is broken down and reformed into the structure of a butterfly. This process typically takes several weeks, after which the butterfly emerges from the chrysalis.")
    ("Greenland is the largest island in the world. True or false?", "True. Greenland is the largest island in the world that is not a continent, covering an area of about 2.16 million square kilometers (836,000 square miles).")
]

def generate_qa_filler(target_tokens: int, seed: int) -> list[dict]:
    """Produce an alternating user/assistant trivia conversation ~target_tokens long."""
    return build_filler_messages(target_tokens, seed, QA_CORPUS)
