import pandas as pd
import os
import random
import msvcrt
from datetime import datetime

class EnglishDictionary:
    def __init__(self, excel_file='dictionary.xlsx'):
        self.excel_file = excel_file
        self.dictionary, self.memory_data = self.load_dictionary()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_key_input(self, prompt=None):
        if prompt:
            print(prompt, end='', flush=True)
        return msvcrt.getch().decode('utf-8').lower()

    def get_display_width(self, text):
        """计算字符串在终端中的实际显示宽度（中文算2个字符）"""
        width = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':
                width += 2
            else:
                width += 1
        return width

    def pad_text(self, text, target_width):
        """填充文本到目标显示宽度"""
        current_width = self.get_display_width(text)
        if current_width >= target_width:
            return text
        return text + ' ' * (target_width - current_width)

    def load_dictionary(self):
        if os.path.exists(self.excel_file):
            try:
                df = pd.read_excel(self.excel_file)
                if 'memory_data' not in df.columns:
                    df['memory_data'] = 0
                if 'last_review' not in df.columns:
                    df['last_review'] = datetime.now().strftime('%Y-%m-%d')
                
                dictionary_data = dict(zip(df['word'], df['meanings']))
                memory_data = dict(zip(df['word'], zip(df['memory_data'], df['last_review'])))
                return dictionary_data, memory_data
            except Exception as e:
                print(f"Error loading dictionary: {e}")
                return {}, {}
        return {}, {}

    def save_dictionary(self):
        if self.dictionary:
            words = list(self.dictionary.keys())
            meanings = list(self.dictionary.values())
            memory_values = []
            last_review_dates = []
            
            for word in words:
                if word in self.memory_data:
                    memory_values.append(self.memory_data[word][0])
                    last_review_dates.append(self.memory_data[word][1])
                else:
                    memory_values.append(0)
                    last_review_dates.append(datetime.now().strftime('%Y-%m-%d'))
            
            df = pd.DataFrame({
                'word': words,
                'meanings': meanings,
                'memory_data': memory_values,
                'last_review': last_review_dates
            })
            df.to_excel(self.excel_file, index=False)

    def get_quiz_words(self):
        """获取需要复习的单词列表"""
        return [word for word, (memory_count, _) in self.memory_data.items() if memory_count < 27]

    def update_memory_data(self, word, is_correct):
        """更新单词的记忆数据"""
        if word in self.memory_data:
            current_count, _ = self.memory_data[word]
            new_count = current_count + 1 if is_correct else 0
        else:
            new_count = 1 if is_correct else 0
        
        self.memory_data[word] = (new_count, datetime.now().strftime('%Y-%m-%d'))

    def add_word(self, word):
        self.clear_screen()
        print(f"=== Add New Word: {word} ===")
        meanings_input = input("Enter meanings (use spaces to separate): ")
        meanings = [m.strip() for m in meanings_input.split() if m.strip()]

        if meanings and not any(m.lower() == 'q' for m in meanings):
            self.dictionary[word.lower()] = '; '.join(meanings)
            self.memory_data[word.lower()] = (0, datetime.now().strftime('%Y-%m-%d'))
            print(f"\nAdded: {word} => {self.dictionary[word.lower()]}")
            self.save_dictionary()
            print("\nPress any key to continue...")
            msvcrt.getch()

    def lookup_word(self, word):
        self.clear_screen()
        print("=== Search Word ===")
        word_lower = word.lower()

        if any(char.isdigit() for char in word):
            print(f"\n{word_lower} is an invalid word")
        elif word_lower in self.dictionary:
            memory_count, _ = self.memory_data.get(word_lower, (0, ''))
            print(f"\n{word} => {self.dictionary[word_lower]}")
            print(f"Memory level: {memory_count}/27")
            if memory_count >= 27:
                print("✓ Mastered! (Excluded from quizzes)")
        else:
            self.add_word(word)
            
        print("\nPress any key to continue...")
        msvcrt.getch()

    def quiz_mode(self):
        quiz_words = self.get_quiz_words()
        
        if not quiz_words:
            self.clear_screen()
            print("=== Vocabulary Quiz ===")
            print("All words have been mastered! 🎉")
            print("No words need review.")
            print("\nPress any key to continue...")
            msvcrt.getch()
            return
        
        score = 0
        total_attempted = 0
        random.shuffle(quiz_words)
        
        for word in quiz_words:
            total_attempted += 1
            self.clear_screen()
            print("=== Vocabulary Quiz ===")
            memory_count, _ = self.memory_data.get(word, (0, ''))
            mastered_words = sum(1 for count, _ in self.memory_data.values() if count >= 27)
            total_words = len(self.memory_data)
            
            print(f"Score: {score}/{total_attempted-1}")
            print(f"Memory: {memory_count}/27 | Mastered: {mastered_words}/{total_words}\n")
            print(word)
            print("-" * 40)
            
            correct_meaning = self.dictionary[word]
            other_words = [w for w in quiz_words if w != word]
            
            # 获取错误选项
            wrong_meanings = []
            if len(other_words) >= 3:
                wrong_words = random.sample(other_words, 3)
                wrong_meanings = [self.dictionary[w] for w in wrong_words]
            else:
                wrong_meanings = ["Unknown meaning", "Incorrect translation", "Wrong answer"]
            
            # 创建并打乱选项
            options = [correct_meaning] + wrong_meanings[:3]
            random.shuffle(options)
            correct_index = options.index(correct_meaning) + 1
            
            # 显示选项
            for idx, option in enumerate(options, 1):
                print(f"{idx}. {option}")
            
            print("\nChoose an option (1-4) or 'q' to quit", end='', flush=True)
            user_choice = self.get_key_input()
            
            if user_choice == 'q':
                break
                
            try:
                choice_num = int(user_choice)
                is_correct = (choice_num == correct_index)
                
                self.update_memory_data(word, is_correct)
                
                self.clear_screen()
                print("=== Vocabulary Quiz ===")
                if is_correct:
                    score += 1
                    new_count, _ = self.memory_data[word]
                    if new_count >= 27:
                        print(f"🎉 Congratulations! '{word}' has been mastered!")
                else:
                    print("✗ Wrong!")
                    print(f"\n{word} => {correct_meaning}")
                    print("\nPress any key for next question...")
                    msvcrt.getch()
                
            except:
                self.clear_screen()
                print("=== Vocabulary Quiz ===")
                print("Invalid input!")
                msvcrt.getch()
            
        
        self.save_dictionary()
        self.clear_screen()
        print("=== Quiz Results ===")
        mastered = sum(1 for count, _ in self.memory_data.values() if count >= 27)
        total = len(self.memory_data)
        print(f"Final score: {score}/{total_attempted-1}")
        print(f"Mastered words: {mastered}/{total}")
        print("\nPress any key to continue...")
        msvcrt.getch()

    def find_word_page(self, search_word):
        """查找以搜索词开头的单词所在的页码"""
        if not self.dictionary:
            return -1
        
        words = sorted(self.dictionary.keys())
        search_word = search_word.lower()
        
        for i, word in enumerate(words):
            if word.lower().startswith(search_word):
                return i // 10
        
        return -1

    def show_all_words(self):
        if not self.dictionary:
            self.clear_screen()
            print("╔" + "═" * 78 + "╗")
            print("║" + "No words in dictionary.".center(78) + "║")
            print("╚" + "═" * 78 + "╝")
            print("\nPress any key to continue...")
            msvcrt.getch()
            return
        
        words = sorted(self.dictionary.items())
        total_pages = (len(words) + 9) // 10
        current_page = 0
        
        while True:
            self.clear_screen()
            print("╔" + "═" * 78 + "╗")
            print("║" + f"All Words (Page {current_page + 1}/{total_pages})".center(78) + "║")
            print("╠" + "═" * 78 + "╣")
            print("║" + " " * 4 + " J: Next page" + " " * 4 + "│" + " " * 4 + "K: Previous page" + " " * 4 + "│" + " " * 4 + "S: Search" + " " * 4 + "│" + " " * 3 + "Q: Quit" + " " * 3 + "║")
            print("╠" + "═" * 78 + "╣")

            print("║ {:^5} │ {:^18} │ {:^38} │ {:^6} ║".format("No.", "Word", "Meaning", "Status"))
            print("╠" + "═" * 7 + "╪" + "═" * 20 + "╪" + "═" * 40 + "╪" + "═" * 8 + "╣")
            
            start_idx = current_page * 10
            end_idx = min(start_idx + 10, len(words))
            
            for i, (word, meaning) in enumerate(words[start_idx:end_idx], start_idx + 1):
                memory_count, _ = self.memory_data.get(word, (0, ''))
                status = "✓" if memory_count >= 27 else f"{memory_count:2d}"
                
                formatted_meaning = '; '.join([m.strip() for m in meaning.split(';')])
                
                # 处理长文本
                if self.get_display_width(formatted_meaning) > 38:
                    temp = ""
                    for char in formatted_meaning:
                        if self.get_display_width(temp + char) <= 35:
                            temp += char
                        else:
                            break
                    formatted_meaning = temp + "..."
                
                padded_meaning = self.pad_text(formatted_meaning, 38)
                
                print("║ {:^5} │ {:<18} │ {} │ {:^6} ║".format(
                    i, word, padded_meaning, status
                ))
            
            print("╠" + "═" * 78 + "╣")
            
            mastered = sum(1 for count, _ in self.memory_data.values() if count >= 27)
            total = len(self.dictionary)
            stats_text = f"Showing {start_idx + 1}-{end_idx} of {total} words | Mastered: {mastered}/{total}"
            print("║" + stats_text.center(78) + "║")
            print("╚" + "═" * 78 + "╝")
            
            user_input = self.get_key_input()
            
            if user_input == 'q':
                break
            elif user_input == 'j' and current_page < total_pages - 1:
                current_page += 1
            elif user_input == 'k' and current_page > 0:
                current_page -= 1
            elif user_input == 's':
                self.clear_screen()
                print("╔" + "═" * 78 + "╗")
                print("║" + "SEARCH WORD (Starts with)".center(78) + "║")
                print("╚" + "═" * 78 + "╝")
                search_term = input("Enter word to search: ").strip().lower()
                
                if search_term:
                    page = self.find_word_page(search_term)
                    if page != -1:
                        current_page = page
                    else:
                        print(f"\nNo word starting with '{search_term}' found.")
                        print("\nPress any key to continue...")
                        msvcrt.getch()
                    
    def show_menu(self):
        self.clear_screen()
        print("====== Welcome to BYD! ======")
        print("=== Build Your Dictionary ===")
        print("=" * 29)
        print("1. Search/Add word")
        print("2. Vocabulary quiz")
        print("3. Show all words")
        print("Q. Exit")
        print("=" * 29)

    def search_word_mode(self):
        self.clear_screen()
        print("=== Search/Add Word ===")
        word = input("Enter word('q' to quit): ").strip()
        if word and word.lower() != 'q':
            self.lookup_word(word)

    def run(self):
        while True:
            self.show_menu()
            
            try:
                choice = self.get_key_input()
                
                if choice == 'q':
                    self.clear_screen()
                    break
                elif choice == '1':
                    self.search_word_mode()
                elif choice == '2':
                    self.quiz_mode()
                elif choice == '3':
                    self.show_all_words()
                else:
                    print("\nInvalid choice. Please enter 1, 2, 3 or Q.")
                    print("\nPress any key to continue...")
                    msvcrt.getch()
                    
            except KeyboardInterrupt:
                self.clear_screen()
                break
            except Exception as e:
                self.clear_screen()
                print(f"An error occurred: {e}")
                print("\nPress any key to continue...")
                msvcrt.getch()

if __name__ == "__main__":
    dictionary = EnglishDictionary()
    dictionary.run()