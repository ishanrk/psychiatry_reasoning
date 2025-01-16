import openai
import json
from collections import defaultdict
import networkx as nx
import matplotlib.pyplot as plt

# Set up OpenAI API key
openai.api_key = 'insert_here' 

def read_case_document(file_path):
    """Reads a psychiatry patient case document and extracts text."""
    with open(file_path, 'r') as file:
        case_text = file.read()
    return case_text

def extract_patient_profile(case_text):
    """Uses ChatGPT to build a structured patient profile from case details."""
    prompt = f"""
    Analyze the following psychiatry patient case and construct a detailed patient profile including:
    - Name (if available)
    - Age
    - Gender
    - Presenting complaint
    - History of presenting illness
    - Past medical history
    - Family history
    - Social history
    - Mental status examination
    - Current medications
    - Any additional relevant details

    Patient Case:
    {case_text}
    
    Provide the output in structured JSON format.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a psychiatrist building a structured case profile."},
                  {"role": "user", "content": prompt}]
    )
    patient_profile = response['choices'][0]['message']['content']
    return json.loads(patient_profile)

def construct_knowledge_graph(profile):
    """Constructs a conceptual knowledge graph from the patient profile."""
    G = nx.DiGraph()
    
    # Add nodes and edges based on patient profile
    # Example: Connecting symptoms, medical history, and potential causes
    G.add_node('Patient', weight=1.0)
    for key, value in profile.items():
        if isinstance(value, dict):
            for sub_key, sub_value in value.items():
                G.add_node(sub_key, weight=0.5)
                G.add_edge('Patient', sub_key, weight=0.8)
                G.add_edge(sub_key, sub_value, weight=0.7)
        else:
            G.add_node(key, weight=0.5)
            G.add_edge('Patient', key, weight=0.8)
            G.add_edge(key, value, weight=0.7)
    
    # Display the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', edge_color='gray', node_size=3000, font_size=10)
    plt.show()
    
    return G

def differential_diagnosis(profile, graph):
    """Finds differential diagnoses based on the patient profile and knowledge graph."""
    prompt = f"""
    Given the following psychiatry patient profile and associated conceptual knowledge graph, list potential differential diagnoses and their justifications:
    
    Patient Profile: {json.dumps(profile)}
    
    Conceptual Knowledge Graph: {str(graph.edges(data=True))}
    
    Provide a ranked list of potential diagnoses with reasoning.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a medical diagnostic assistant."},
                  {"role": "user", "content": prompt}]
    )
    return response['choices'][0]['message']['content']

def main():
    # Example case file (replace with your own file)
    case_file_path = 'psychiatry_case.txt'
    
    # Step 1: Read the case document
    case_text = read_case_document(case_file_path)
    
    # Step 2: Build a patient profile
    patient_profile = extract_patient_profile(case_text)
    print("Patient Profile:", json.dumps(patient_profile, indent=4))
    
    # Step 3: Construct a conceptual knowledge graph (CKG)
    knowledge_graph = construct_knowledge_graph(patient_profile)
    
    # Step 4: Perform differential diagnosis using the CKG
    differential_diagnoses = differential_diagnosis(patient_profile, knowledge_graph)
    print("Differential Diagnoses and Final Condition Assessment:")
    print(differential_diagnoses)

# Execute the main function
if __name__ == "__main__":
    main()
