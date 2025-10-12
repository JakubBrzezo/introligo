"""String utility functions.

This module provides common string manipulation utilities including
case conversion, counting, and validation functions.

Example:
    Basic usage of string utilities::

        from string_utils import capitalize_words, count_vowels

        text = "hello world"
        result = capitalize_words(text)
        print(result)  # "Hello World"

        vowel_count = count_vowels(text)
        print(vowel_count)  # 3
"""


def capitalize_words(text: str) -> str:
    """Capitalize the first letter of each word in a string.

    Args:
        text: The input string to process.

    Returns:
        A new string with each word capitalized.

    Example:
        >>> capitalize_words("hello world")
        'Hello World'
        >>> capitalize_words("python programming")
        'Python Programming'
    """
    return " ".join(word.capitalize() for word in text.split())


def count_vowels(text: str) -> int:
    """Count the number of vowels in a string.

    Args:
        text: The input string to analyze.

    Returns:
        The total number of vowels (a, e, i, o, u) in the string,
        case-insensitive.

    Example:
        >>> count_vowels("Hello World")
        3
        >>> count_vowels("Python")
        1
    """
    vowels = "aeiouAEIOU"
    return sum(1 for char in text if char in vowels)


def reverse_string(text: str) -> str:
    """Reverse a string.

    Args:
        text: The input string to reverse.

    Returns:
        The reversed string.

    Example:
        >>> reverse_string("hello")
        'olleh'
        >>> reverse_string("Python")
        'nohtyP'
    """
    return text[::-1]


def is_palindrome(text: str) -> bool:
    """Check if a string is a palindrome.

    A palindrome reads the same forwards and backwards, ignoring
    spaces, punctuation, and case.

    Args:
        text: The input string to check.

    Returns:
        True if the string is a palindrome, False otherwise.

    Example:
        >>> is_palindrome("racecar")
        True
        >>> is_palindrome("hello")
        False
        >>> is_palindrome("A man a plan a canal Panama")
        True
    """
    # Remove non-alphanumeric characters and convert to lowercase
    cleaned = "".join(char.lower() for char in text if char.isalnum())
    return cleaned == cleaned[::-1]


def word_count(text: str) -> int:
    """Count the number of words in a string.

    Words are defined as sequences of characters separated by whitespace.

    Args:
        text: The input string to analyze.

    Returns:
        The number of words in the string.

    Example:
        >>> word_count("Hello world")
        2
        >>> word_count("Python is great")
        3
    """
    return len(text.split())
