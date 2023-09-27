import re

def load_text_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            return text
    except FileNotFoundError:
        print("Файл не найден")
        return None

def preprocess_text(text):
    # Убираем лишние символы, оставляем только буквы и пробелы
    text = re.sub(r'[^а-яА-Яa-zA-Z\s.!?]', '', text)
    # Заменяем множественные пробелы одним пробелом
    text = re.sub(r'\s+', ' ', text)
    # Убираем пробелы в начале и конце текста
    text = text.strip()
    return text

def split_text_into_sentences(text):
    # Разбиваем текст на предложения, учитывая разные варианты окончания
    sentences = re.split(r'[.!?]+', text)
    # Удаляем пустые предложения (могут появиться после разбиения)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    return sentences

def split_sentence_into_words(sentence):
    # Разбиваем предложение на слова по пробелам
    words = sentence.split()
    return words

def main():
    file_path = 'txt.txt'  # Замените на путь к вашему файлу
    text = load_text_from_file(file_path)

    if text:
        text = preprocess_text(text)

        sentences = split_text_into_sentences(text)
        words = [split_sentence_into_words(sentence) for sentence in sentences]

        # Вычисляем количество слов
        all_words = [word for sentence_words in words for word in sentence_words]
        unique_words = set(all_words)

        # Вычисляем количество предложений
        num_sentences = len(sentences)

        # Выводим результаты
        print(f"Общее количество слов: {len(all_words)}")
        print(f"Уникальные слова: {len(unique_words)}")
        print(f"Количество предложений: {num_sentences}")

if __name__ == "__main__":
    main()
