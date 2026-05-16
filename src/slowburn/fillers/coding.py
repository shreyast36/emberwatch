"""Innocuous coding-conversation filler.

Owner: Binjie. See ROLES.md.
"""

from slowburn.fillers.base import build_filler_messages

# 100% safe, hand-authored programming Q&A pairs
CODING_CORPUS = [
    ("How do I reverse a string in Python?", "You can reverse a string using slicing: `my_string[::-1]`."),
    ("What is the difference between a list and a tuple?", "Lists are mutable, meaning they can be changed after creation. Tuples are immutable and cannot be changed."),
    ("Write a CSS snippet to center a div.", "You can use flexbox: `display: flex; justify-content: center; align-items: center;`."),
    ("What does the 'git pull' command do?", "It fetches changes from a remote repository and merges them into your current branch."),
    ("How do I check if a key exists in a Python dictionary?", "You can use the `in` keyword: `if key in my_dict:`."),
    ("Explain what a Promise is in JavaScript.", "A Promise is an object representing the eventual completion or failure of an asynchronous operation."),
    ("How do you declare a constant in Go?", "You declare a constant in Go using the `const` keyword, like `const Pi = 3.14`."),
    ("What is a foreign key in SQL?", "A foreign key is a column or group of columns in a relational database table that provides a link between data in two tables."),
    ("How do I read a file line by line in bash?", "You can use a while loop with read: `while read line; do echo $line; done < file.txt`."),
    ("Show me how to instantiate a class in Java.", "You use the `new` keyword, for example: `MyClass obj = new MyClass();`."),
    ("Write a Python function to calculate the Fibonacci sequence.", "Here is a recursive approach:\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```\nFor larger numbers, an iterative approach or memoization is much more efficient."),
    ("How do I parse a JSON string in JavaScript?", "You use `JSON.parse()`. For example:\n```javascript\nconst jsonString = '{\"name\": \"Alice\", \"age\": 30}';\nconst user = JSON.parse(jsonString);\nconsole.log(user.name);\n```"),
    ("Explain the concept of dependency injection.", "Dependency injection is a design pattern where an object receives other objects that it depends on (called dependencies) rather than creating them itself. This promotes loose coupling and makes code easier to test."),
    ("Can you show me a basic Dockerfile for a Node.js app?", "Certainly! Here is a basic example:\n```dockerfile\nFROM node:18-alpine\nWORKDIR /app\nCOPY package*.json ./\nRUN npm install\nCOPY . .\nEXPOSE 3000\nCMD [\"npm\", \"start\"]\n```"),
    ("What does the `yield` keyword do in Python?", "`yield` pauses the execution of a function and returns a value to the caller, saving the state of the function. When the function is called again, execution resumes right after the `yield` statement. This is used to create generators."),
    ("How do I fix a 'detached HEAD' state in Git?", "A detached HEAD means you have checked out a specific commit rather than a branch. To fix it and save your work, you can create a new branch from this state using `git checkout -b <new-branch-name>`."),
    ("How do I create a basic functional component in React?", "Here is a simple functional component:\n```jsx\nimport React from 'react';\n\nfunction Greeting({ name }) {\n  return <h1>Hello, {name}!</h1>;\n}\n\nexport default Greeting;\n```"),
    ("What is an INNER JOIN in SQL?", "An INNER JOIN combines rows from two tables based on a related column. It only returns records that have matching values in both tables. For example: `SELECT * FROM Orders INNER JOIN Customers ON Orders.CustomerID = Customers.ID;`"),
    ("Show me an example of class inheritance in Python.", "Here is an example:\n```python\nclass Animal:\n    def speak(self):\n        pass\n\nclass Dog(Animal):\n    def speak(self):\n        return 'Woof!'\n\nmy_dog = Dog()\nprint(my_dog.speak())\n```"),
    ("What is the basic structure of an HTML5 document?", "An HTML5 document structure looks like this:\n```html\n<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n    <meta charset=\"UTF-8\">\n    <title>Document</title>\n</head>\n<body>\n    <p>Content goes here.</p>\n</body>\n</html>\n```"),
    ("How do I temporarily save my uncommitted changes in Git?", "You can use the `git stash` command. This will save your local modifications away and revert the working directory to match the HEAD commit. You can re-apply them later with `git stash pop`."),
    ("What is a regular expression used for?", "Regular expressions, or regex, are sequences of characters that define a search pattern. They are highly useful for string searching, text matching, and validation tasks, such as checking if a string matches a standard email format."),
    ("Write a Hello World program in C++.", "Here is the standard C++ Hello World:\n```cpp\n#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    return 0;\n}\n```"),
    ("How do I change the background color of a button when hovering over it?", "You use the `:hover` pseudo-class in CSS. For example:\n```css\nbutton:hover {\n    background-color: blue;\n}\n```"),
    ("How do I use the map function on an array in JavaScript?", "The map function creates a new array populated with the results of calling a provided function on every element in the calling array. Example:\n```javascript\nconst numbers = [1, 2, 3];\nconst doubled = numbers.map(x => x * 2);\n```"),
    ("What does the chmod command do in Linux?", "The `chmod` command stands for 'change mode', and it is used to change the access permissions of file system objects, directories, and files in Unix-like operating systems."),
    ("What is a list comprehension in Python?", "List comprehensions offer a shorter syntax to create a new list based on the values of an existing list. Example: `squares = [x**2 for x in range(10)]`."),
    ("How do I list all running containers in Docker?", "You can list all running Docker containers by executing `docker ps` in your terminal. To see all containers, including stopped ones, use `docker ps -a`."),
    ("How do you declare a mutable variable in Rust?", "By default, variables in Rust are immutable. To make them mutable, you add the `mut` keyword. Example: `let mut x = 5;`"),
    ("What is the difference between an interface and a type alias in TypeScript?", "Both can be used to describe the shape of an object. A key difference is that interfaces are always extendable (via declaration merging), whereas type aliases cannot be reopened to add new properties."),
    ("What does `NaN` mean in JavaScript?", "`NaN` stands for 'Not-a-Number'. It is a property of the global object representing a value that is not a legal number."),
    ("How do I create a virtual environment in Python?", "You can create a virtual environment using the `venv` module. Run `python -m venv myenv` in your terminal. To activate it on Windows, use `myenv\\Scripts\\activate`, and on macOS/Linux, use `source myenv/bin/activate`."),
    ("Write a bash script to iterate over all `.txt` files in a directory.", "Here is a simple bash loop:\n```bash\nfor file in *.txt; do\n    echo \"Processing $file\"\n    cat \"$file\"\ndone\n```"),
    ("What is the `box-sizing: border-box` property in CSS?", "It tells the browser to account for any border and padding in the values you specify for an element's width and height, preventing the element from expanding beyond its defined dimensions."),
    ("How do you add a new element to the end of an array in PHP?", "In PHP, arrays are dynamic. You can append an element by assigning a value without specifying an index, like this: `$myArray[] = \"new value\";`, or by using the `array_push()` function."),
    ("How do I use the `reduce` method in JavaScript?", "The `reduce` method executes a reducer function on each element of the array, resulting in a single output value. For example, to sum an array of numbers:\n```javascript\nconst numbers = [1, 2, 3, 4];\nconst sum = numbers.reduce((accumulator, currentValue) => accumulator + currentValue, 0);\nconsole.log(sum); // Output: 10\n```"),
    ("What does SQL stand for?", "SQL stands for Structured Query Language."),
    ("How do I remove the last commit in Git but keep my changes?", "You can use `git reset --soft HEAD~1`. This will undo the last commit but leave your working directory and staging area exactly as they were."),
    ("Can you show me how to write a simple GET request using the `fetch` API?", "Certainly. Here is an example of a basic GET request:\n```javascript\nfetch('https://api.example.com/data')\n  .then(response => response.json())\n  .then(data => console.log(data))\n  .catch(error => console.error('Error fetching data:', error));\n```"),
    ("What is a Goroutine in Go?", "A Goroutine is a lightweight thread managed by the Go runtime, used to perform tasks concurrently."),
    ("What is the difference between `==` and `===` in JavaScript?", "`==` checks for value equality and performs type coercion if the types are different. `===` checks for strict equality, meaning both the value and the type must be exactly the same."),
    ("How do I read a JSON file in Node.js?", "You can use the built-in `fs` module to read the file, and then parse it. Example:\n```javascript\nconst fs = require('fs');\n\nfs.readFile('data.json', 'utf8', (err, data) => {\n  if (err) throw err;\n  const json = JSON.parse(data);\n  console.log(json);\n});\n```"),
    ("What is the `len()` function in Python used for?", "The `len()` function returns the number of items in an object, such as the number of characters in a string or elements in a list."),
    ("What is the purpose of the `__init__` method in Python?", "The `__init__` method is the constructor in Python. It is automatically called when a new instance of a class is created, and it is used to initialize the object's attributes."),
    ("How do I create an abstract class in C#?", "You create an abstract class by using the `abstract` keyword. Methods inside it can also be abstract, meaning they have no body and must be implemented by derived classes:\n```csharp\npublic abstract class Shape\n{\n    public abstract void Draw();\n}\n```"),
    ("What command lists directories in a Unix shell?", "The `ls` command is used to list directory contents. Adding the `-l` flag provides a detailed format."),
    ("How do I find the length of a string in C?", "In standard C, you can use the `strlen` function from the `<string.h>` library. For example: `size_t len = strlen(\"hello\");`."),
    ("What is a dictionary comprehension in Python?", "It is a concise way to create dictionaries from iterables. For example, to create a dictionary mapping numbers to their cubes:\n```python\ncubes = {x: x**3 for x in range(5)}\nprint(cubes) # {0: 0, 1: 1, 2: 8, 3: 27, 4: 64}\n```"),
    ("What is the default port for an HTTP server?", "The default port for HTTP is 80, while the default port for HTTPS is 443."),
    ("How do I reverse an array in Java?", "You can use the `Collections.reverse()` method if it is a list. If it is a primitive array, you can either loop through it and swap elements symmetrically, or convert it using `Arrays.asList()` and then reverse it.")
]

def generate_coding_filler(target_tokens: int, seed: int) -> list[dict]:
    """Produce an alternating user/assistant coding conversation ~target_tokens long."""
    return build_filler_messages(target_tokens, seed, CODING_CORPUS)
