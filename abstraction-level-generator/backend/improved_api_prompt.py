def generate_prompt(raw_question, level):
    prompt = f"""
Given the following raw question, generate an abstraction at level {level} (0-7).
Follow these guidelines for each abstraction level:

Raw Question: "{raw_question}"

Abstraction Levels:
0. Concrete: Specific instance with all original details.
1. Basic Abstraction: Replace specific values with variables, maintain original structure.
2. Structural Abstraction: Identify and abstract common patterns or structures.
3. Functional Abstraction: Focus on purpose/function of elements rather than specific nature.
4. Conceptual Abstraction: Extract core concepts and principles, remove domain-specific details.
5. Meta-Abstract: Create a framework for defining and manipulating abstract structures.
6. Universal Abstract: Identify fundamental principles applying across multiple domains.
7. Philosophical Abstract: Explore the fundamental nature of concepts involved.

For level {level}, provide:
1. Ideal Representation: A description of how the problem should be represented at this level.
2. Generated Question: An abstract version of the original question at this level.
3. Score: A float between 0 and 7 indicating how well the generated question matches the ideal representation.
4. Variables: A string which may or may not contain a dictionary of key variables and their sample values relevant to this abstraction level.

Format your response as a JSON object with the following structure:
{{
    "ideal_representation": "...",
    "generated_question": "...",
    "score": 0.0,
    "variables": "..."
}}

Ensure that your response is a valid JSON object and includes all required fields.
"""
    return prompt

# Example usage
raw_question = "A jar contains 1 green button, 2 yellow buttons, 4 red buttons, and 8 blue buttons. What is the probability of taking each color button from the jar?"
level = 2
prompt = generate_prompt(raw_question, level)
print(prompt)