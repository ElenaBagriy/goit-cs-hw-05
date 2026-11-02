import requests
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
import string


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        return response.text
    except requests.RequestException:
        return None


# Функція для видалення знаків пунктуації
def remove_punctuation(text):
    return text.lower().translate(str.maketrans("", "", string.punctuation))


# Функція Map: розбиває текст на слова та створює пари (слово, 1)
def map_function(word):
    return word, 1


# Функція Shuffle: групує однакові слова разом
def shuffle_function(mapped_values):
    shuffled = defaultdict(list)
    for key, value in mapped_values:
        shuffled[key].append(value)
    return shuffled.items()


# Функція Reduce: підраховує кількість повторень кожного слова
def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


# Виконання MapReduce з використанням багатопотоковості
def map_reduce(text):
    # Видалення знаків пунктуації
    text = remove_punctuation(text)
    # Розділення тексту на частини для обробки в потоках
    words = text.split()
    # Паралельний Мапінг
    with ThreadPoolExecutor() as executor:
        mapped_values = list(executor.map(map_function, words))

    # Крок 2: Shuffle
    shuffled_values = shuffle_function(mapped_values)

    # Паралельна Редукція
    with ThreadPoolExecutor() as executor:
        reduced_values = list(executor.map(reduce_function, shuffled_values))

    return dict(reduced_values)


# Функція для візуалізації найчастіше вживаних слів
def visualize_top_words(word_counts, top_n=10):
    # Сортування слів за частотою використання у порядку спадання
    top_words = sorted(
        word_counts.items(),
        key=lambda item: item[1],
        reverse=True
    )[:top_n]

    # Отримання окремих списків слів та їх частоти
    words = [item[0] for item in top_words]
    counts = [item[1] for item in top_words]

    # Побудова горизонтальної діаграми
    plt.figure(figsize=(12, 6))
    plt.barh(words, counts)
    plt.xlabel('Frequency')
    plt.ylabel('Words')
    plt.title(f'Top {top_n} Most Frequent Words')

    # Розміщення найчастіше вживаних слів зверху
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()


# Головний блок програми
if __name__ == "__main__":
    # URL-адреса тексту для аналізу
    url = "https://gutenberg.net.au/ebooks01/0100021.txt"
    text = get_text(url)
    if text:
        # Виконання MapReduce на вхідному тексті
        result = map_reduce(text)
        # Візуалізація 10 найчастіше вживаних слів
        visualize_top_words(result, top_n=10)
    else:
        print("Помилка: Не вдалося отримати вхідний текст.")

