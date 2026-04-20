import unittest

from genai import summarize_patient_sheet

class Test_test_gen(unittest.TestCase):

    def setUp(self):
        self.test_info = "Patient Symptoms: I've developed these round, scaly patches on my arms and legs that are really itchy. They started small but have been spreading. The patches are slightly raised, reddish, and have a silvery-white scale on top. They get worse when I'm stressed and during winter months. I've tried over-the-counter hydrocortisone cream but it only helps temporarily."

    def test_zeroShot(self):

        (prompt, result) = summarize_patient_sheet(self.test_info, rag=False);
        print("Prompt:")
        print(prompt)
        print()
        print("Result:")
        print(result)

    def test_zeroShotWithRAG(self):
        (prompt, result) = summarize_patient_sheet(self.test_info, rag=True);
        print("Prompt:")
        print(prompt)
        print()
        print("Result:")
        print(result)

    def test_oneShotWithRAG(self):
        (prompt, result) = summarize_patient_sheet(self.test_info, rag=True, preprompt="Example:\nQ:{'urgency': 'Non-Urgent'}I can't feel my legs.\nA:The patient experiences an urgent symptom. The symptoms are highly suggestive of **eripheral neuropathy**.");
        print("Prompt:")
        print(prompt)
        print()
        print("Result:")
        print(result)



if __name__ == '__main__':
    unittest.main()
