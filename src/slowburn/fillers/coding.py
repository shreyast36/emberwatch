"""Innocuous coding-conversation filler.

Owner: Binjie. See ROLES.md.
"""

import random

import tiktoken

_ENCODER = tiktoken.get_encoding("cl100k_base")

_PAIRS: list[tuple[str, str]] = [
    (
        "How do I reverse a list in Python?",
        "Use slicing: `my_list[::-1]` returns a new reversed list without modifying the original. "
        "If you want to reverse in place, call `my_list.reverse()`. "
        "Slicing is preferred when you need to keep the original list intact.",
    ),
    (
        "What is a list comprehension and when should I use one?",
        "A list comprehension is a concise way to build a list: `[expr for item in iterable if condition]`. "
        "Use one when the logic is simple enough to read in a single line. "
        "For complex transformations, a regular for-loop is clearer. "
        "Example: `squares = [x**2 for x in range(10) if x % 2 == 0]`.",
    ),
    (
        "Can you explain Python decorators with a simple example?",
        "A decorator is a function that wraps another function to extend its behaviour. "
        "Example:\n```python\ndef log_call(func):\n    def wrapper(*args, **kwargs):\n        print(f'Calling {func.__name__}')\n        return func(*args, **kwargs)\n    return wrapper\n\n@log_call\ndef greet(name):\n    return f'Hello, {name}'\n```\n"
        "When you call `greet('Alice')`, the wrapper prints the log line first, then calls the original.",
    ),
    (
        "What is the difference between `==` and `is` in Python?",
        "`==` checks value equality — whether two objects have the same value. "
        "`is` checks identity — whether two variables point to the exact same object in memory. "
        "Use `==` for comparing values. Use `is` only for singletons like `None`, `True`, and `False`. "
        "Example: `[] == []` is True, but `[] is []` is False because they are different objects.",
    ),
    (
        "How do context managers and the `with` statement work?",
        "A context manager handles setup and teardown around a block of code. "
        "The `with` statement calls `__enter__` on entry and `__exit__` on exit (even if an exception occurs). "
        "Example: `with open('file.txt') as f:` opens the file and guarantees it is closed afterwards. "
        "You can create your own with `@contextlib.contextmanager` or by implementing `__enter__` and `__exit__`.",
    ),
    (
        "What is a generator and how is it different from a list?",
        "A generator produces values one at a time using `yield`, keeping only the current value in memory. "
        "A list stores all values at once. Use a generator when the sequence is large or infinite. "
        "Example: `def count_up(n): yield from range(n)` — calling `next()` on the generator advances it. "
        "Generator expressions: `(x**2 for x in range(1000))` — note the parentheses instead of brackets.",
    ),
    (
        "How do I use type hints in Python function signatures?",
        "Add annotations after parameter names and after `->` for the return type:\n"
        "```python\ndef add(a: int, b: int) -> int:\n    return a + b\n```\n"
        "For optional values use `int | None` (Python 3.10+). "
        "For collections: `list[str]`, `dict[str, int]`. Type hints are not enforced at runtime but "
        "help editors and tools like mypy catch errors.",
    ),
    (
        "What are dataclasses and when should I use them?",
        "Dataclasses auto-generate `__init__`, `__repr__`, and `__eq__` from annotated class attributes:\n"
        "```python\nfrom dataclasses import dataclass\n\n@dataclass\nclass Point:\n    x: float\n    y: float\n```\n"
        "Use them when your class is primarily a data container. For immutable data, add `frozen=True`. "
        "For more complex behaviour, a regular class or Pydantic model may be more appropriate.",
    ),
    (
        "How do I sort a list of dictionaries by a specific key?",
        "Use `sorted()` with a `key` function:\n"
        "```python\npeople = [{'name': 'Bob', 'age': 30}, {'name': 'Alice', 'age': 25}]\n"
        "by_age = sorted(people, key=lambda p: p['age'])\n```\n"
        "For descending order add `reverse=True`. To sort in place use `list.sort(key=...)`. "
        "For multiple keys: `key=lambda p: (p['age'], p['name'])`.",
    ),
    (
        "What is a closure in Python?",
        "A closure is a function that captures variables from its enclosing scope even after that scope has finished. "
        "Example:\n```python\ndef make_multiplier(n):\n    def multiply(x):\n        return x * n\n    return multiply\n\ndouble = make_multiplier(2)\nprint(double(5))  # 10\n```\n"
        "Closures are useful for factories and callbacks where you need to carry state without a class.",
    ),
    (
        "How does exception handling work in Python?",
        "Use `try / except / else / finally`:\n"
        "```python\ntry:\n    result = 10 / x\nexcept ZeroDivisionError:\n    print('Cannot divide by zero')\nexcept (TypeError, ValueError) as e:\n    print(f'Bad input: {e}')\nelse:\n    print(f'Result: {result}')\nfinally:\n    print('Always runs')\n```\n"
        "Catch the most specific exceptions first. Avoid bare `except:` — it hides bugs.",
    ),
    (
        "What are f-strings and how do they compare to `.format()`?",
        "F-strings (Python 3.6+) embed expressions directly in string literals:\n"
        "```python\nname = 'Alice'\nage = 30\nprint(f'{name} is {age} years old')\n```\n"
        "They are faster and more readable than `.format()` or `%` formatting. "
        "You can include any expression: `f'{2 + 2}'`, `f'{obj.method()}'`, `f'{value:.2f}` for floats.",
    ),
    (
        "How do I read and write files in Python?",
        "Reading:\n```python\nwith open('data.txt', 'r', encoding='utf-8') as f:\n    content = f.read()\n    lines = f.readlines()\n```\n"
        "Writing:\n```python\nwith open('output.txt', 'w', encoding='utf-8') as f:\n    f.write('Hello\\n')\n```\n"
        "Always use `with` so the file is closed automatically. Use `'a'` mode to append.",
    ),
    (
        "What is `*args` and `**kwargs` in Python function definitions?",
        "`*args` collects extra positional arguments into a tuple; `**kwargs` collects extra keyword "
        "arguments into a dictionary:\n"
        "```python\ndef log(*args, **kwargs):\n    print(args)\n    print(kwargs)\n\nlog(1, 2, name='Alice', level='info')\n```\n"
        "Use them to write flexible functions. When calling, `*iterable` unpacks positional args.",
    ),
    (
        "How do I use `map()` and `filter()` in Python?",
        "`map(func, iterable)` applies `func` to every element; `filter(func, iterable)` keeps elements "
        "where `func` returns truthy:\n"
        "```python\nnumbers = [1, 2, 3, 4, 5]\nsquares = list(map(lambda x: x**2, numbers))\nevens   = list(filter(lambda x: x % 2 == 0, numbers))\n```\n"
        "In most cases a list comprehension is more readable, but `map`/`filter` are handy with built-ins like `str`.",
    ),
]


def generate_coding_filler(target_tokens: int, seed: int) -> list[dict]:
    if target_tokens == 0:
        return []
    rng = random.Random(seed)
    shuffled = list(_PAIRS)
    rng.shuffle(shuffled)
    messages: list[dict] = []
    total = 0
    idx = 0
    while total < target_tokens:
        q, a = shuffled[idx % len(shuffled)]
        idx += 1
        messages.append({"role": "user", "content": q})
        messages.append({"role": "assistant", "content": a})
        total += len(_ENCODER.encode(q)) + len(_ENCODER.encode(a))
    return messages
