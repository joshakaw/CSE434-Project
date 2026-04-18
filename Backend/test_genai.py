import unittest

from genai import summarize_patient_sheet

class Test_test_genai(unittest.TestCase):
    def test_A(self):

        (prompt, result) = summarize_patient_sheet("Patient Symptoms: I've developed these round, scaly patches on my arms and legs that are really itchy. They started small but have been spreading. The patches are slightly raised, reddish, and have a silvery-white scale on top. They get worse when I'm stressed and during winter months. I've tried over-the-counter hydrocortisone cream but it only helps temporarily.");
        print("Prompt:")
        print(prompt)
        print()
        print("Result:")
        print(result)

if __name__ == '__main__':
    unittest.main()
