import json
from bs4 import BeautifulSoup
import re

def load_correct_answers(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)

def extract_answers_from_html(html_file):
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    questions = []
    for question_panel in soup.find_all('div', class_='question-pnl'):
        question_data = {}
        
        # Extract question ID
        question_id_td = question_panel.find('td', string=lambda text: text and 'Question ID :' in text)
        if not question_id_td:
            continue
        question_id = question_id_td.find_next('td').text.strip()
        question_data['question_id'] = question_id
        
        # Extract option IDs
        option_ids = []
        valid_options = True
        for i in range(1, 5):
            option_td = question_panel.find('td', string=lambda text: text and f'Option {i} ID :' in text)
            if not option_td:
                valid_options = False
                break
            option_id = option_td.find_next('td').text.strip()
            option_ids.append(option_id)
        
        if not valid_options:
            continue
            
        question_data['option_ids'] = option_ids
        
        # Extract chosen option
        chosen_td = question_panel.find('td', string=lambda text: text and 'Chosen Option :' in text)
        if not chosen_td:
            continue
            
        chosen_value = chosen_td.find_next('td').text.strip()
        if chosen_value != '--':
            question_data['chosen_option'] = int(chosen_value)
            question_data['chosen_option_id'] = option_ids[int(chosen_value) - 1]
        else:
            question_data['chosen_option'] = None
            question_data['chosen_option_id'] = None
        
        questions.append(question_data)
    
    return questions

def check_answers(correct_answers, student_answers):
    results = {
        'correct': [],
        'incorrect': [],
        'not_answered': [],
        'total_questions': len(student_answers),
        'total_correct': 0,
        'total_incorrect': 0,
        'total_not_answered': 0
    }
    
    for answer in student_answers:
        q_id = answer['question_id']
        if q_id not in correct_answers:
            continue
            
        if answer['chosen_option'] is None:
            results['not_answered'].append(q_id)
            results['total_not_answered'] += 1
            continue
            
        correct_option_id = correct_answers[q_id]
        if answer['chosen_option_id'] == correct_option_id:
            results['correct'].append(q_id)
            results['total_correct'] += 1
        else:
            results['incorrect'].append(q_id)
            results['total_incorrect'] += 1
    
    return results

def print_results(results):
    print("\nResults Summary:")
    print("-" * 50)
    print(f"Total Questions: {results['total_questions']}")
    print(f"Correct Answers: {results['total_correct']}")
    print(f"Incorrect Answers: {results['total_incorrect']}")
    print(f"Not Answered: {results['total_not_answered']}")
    
    print("\nCorrect Questions:")
    print("-" * 50)
    for q_id in results['correct']:
        print(f"Question ID: {q_id}")
    
    print("\nIncorrect Questions:")
    print("-" * 50)
    for q_id in results['incorrect']:
        print(f"Question ID: {q_id}")
    
    print("\nNot Answered Questions:")
    print("-" * 50)
    for q_id in results['not_answered']:
        print(f"Question ID: {q_id}")

def main():
    try:
        correct_answers = load_correct_answers('list.json')
        student_answers = extract_answers_from_html('ZZ12200290_2083O2595S5D232E1.html')
        if not student_answers:
            print("No valid questions found in the HTML file.")
            return
        results = check_answers(correct_answers, student_answers)
        print_results(results)
    except FileNotFoundError as e:
        print(f"Error: Could not find file - {e.filename}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
