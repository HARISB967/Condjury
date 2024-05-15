import pymongo
import PySimpleGUI as sg

client = pymongo.MongoClient("mongodb+srv://gowtham07:gowtham07@dacluster.vsr0h6v.mongodb.net/")
db = client["dacluster"]
collection = db["judgements"]

class Judge:
    def __init__(self, name, probability, choice):
        self.name = name
        self.probability = probability
        self.choice = choice

def calculate_relative_probabilities(judges):
    total_correct_prob = sum(judge.probability for judge in judges)
    convict_prob = sum(judge.probability for judge in judges if judge.choice == "Convict") / total_correct_prob
    acquit_prob = sum(judge.probability for judge in judges if judge.choice == "Acquit") / total_correct_prob
    return convict_prob, acquit_prob

def provide_verdict(judges):
    convict_prob, acquit_prob = calculate_relative_probabilities(judges)
    if convict_prob > acquit_prob:
        return "Sentence Guilty"
    elif acquit_prob > convict_prob:
        return "Leave Innocent"
    else:
        return "Tie"

def display_decision_signal(judge):
    sg.popup(f"{judge.name} signals: '{judge.choice}'")

judge_layout = [
    [sg.Text('Judge Name:'), sg.Input(key='-JUDGE_NAME-', size=(20, 1))],
    [sg.Text('Choice:'), sg.Combo(['Convict', 'Acquit'], default_value='Convict', key='-JUDGE_CHOICE-', size=(10, 1))],
    [sg.Text('Probability:'), sg.Input(key='-JUDGE_PROB-', size=(10, 1))],
    [sg.Button('Next')]
]
window = sg.Window('Condjury Game', judge_layout)

judges = []
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        break
    if event == 'Next':
        judge_name = values['-JUDGE_NAME-']
        judge_choice = values['-JUDGE_CHOICE-']
        judge_prob = float(values['-JUDGE_PROB-'])
        judges.append(Judge(judge_name, judge_prob, judge_choice))
        if len(judges) == 3:
            break
        judge_layout = [
            [sg.Text(f'Judge {len(judges)+1} Details')],
            [sg.Text('Judge Name:'), sg.Input(key='-JUDGE_NAME-', size=(20, 1))],
            [sg.Text('Choice:'), sg.Combo(['Convict', 'Acquit'], default_value='Convict', key='-JUDGE_CHOICE-', size=(10, 1))],
            [sg.Text('Probability:'), sg.Input(key='-JUDGE_PROB-', size=(10, 1))],
            [sg.Button('Next')]
        ]
        window.close()
        window = sg.Window('Condjury Game', judge_layout)

window.close()

convict_prob, acquit_prob = calculate_relative_probabilities(judges)
sg.popup(f"Relative Probability of Convict: {convict_prob}\nRelative Probability of Acquit: {acquit_prob}")

for judge in judges:
    display_decision_signal(judge)

for i, judge in enumerate(judges):
    change_decision = sg.popup_yes_no(f"{judge.name}, do you want to change your decision?")
    if change_decision == 'Yes':
        new_choice = sg.popup_get_text(f"Enter new decision for {judge.name} (Convict/Acquit):", default_text=judge.choice, keep_on_top=True)
        if new_choice in ['Convict', 'Acquit']:
            judge.choice = new_choice
        else:
            sg.popup_error("Invalid decision entered.")
            continue
        new_probability = float(sg.popup_get_text(f"Enter probability of correctness for {judge.name}:"))
        judge.probability = new_probability
convict_prob, acquit_prob = calculate_relative_probabilities(judges)
sg.popup(f"Updated Relative Probability of Convict: {convict_prob}\nUpdated Relative Probability of Acquit: {acquit_prob}")

for judge in judges:
    display_decision_signal(judge)

for i, judge in enumerate(judges):
    change_decision = sg.popup_yes_no(f"{judge.name}, do you want to reconsider your decision?")
    if change_decision == 'Yes':
        new_choice = sg.popup_get_text(f"Enter new decision for {judge.name} (Convict/Acquit):", default_text=judge.choice, keep_on_top=True)
        if new_choice in ['Convict', 'Acquit']:
            judge.choice = new_choice
        else:
            sg.popup_error("Invalid decision entered.")
            continue
        new_probability = float(sg.popup_get_text(f"Enter probability of correctness for {judge.name}:"))
        judge.probability = new_probability
convict_prob, acquit_prob = calculate_relative_probabilities(judges)
sg.popup(f"Updated Relative Probability of Convict: {convict_prob}\nUpdated Relative Probability of Acquit: {acquit_prob}")

for judge in judges:
    display_decision_signal(judge)

verdict = provide_verdict(judges)
sg.popup(f"Final Verdict based on Condorcet Jury theorem: {verdict}")

data = {
    "stage_1_outcome": {"convict_prob": convict_prob, "acquit_prob": acquit_prob},
    "stage_2_outcome": {"judges_decisions": [judge.choice for judge in judges]},
    "stage_3_outcome": {"updated_convict_prob": convict_prob, "updated_acquit_prob": acquit_prob, "final_verdict": verdict}
}
# Insert data into MongoDB
collection.insert_one(data)

# Close MongoDB client connection
client.close()
