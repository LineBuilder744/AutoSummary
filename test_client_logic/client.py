import requests
import json
import sys
import argparse

def generate_summary(text):

    server_url="http://localhost:8000"
    """
    Sends a request to the server to generate a summary of the provided text.
    
    Args:
        text (str): The text to summarize
        api_token (str, optional): DeepSeek API token
        server_url (str): The URL of the server
        
    Returns:
        str: The generated summary
    """
    # Format the prompt according to the specified template
    prompt = f"""Make me a brief summary of the text. Divide it into small pieces, which have their own subtitles and text, and send me it in this format:
            <summary>
                <summary_piece>
                    <subtitle>
                        Subtitle (or defenition or date or something else)
                    </subtitle>
                    <text>
                        Text of the paragraph (or defenition or date or something else)
                    </text>
                    <formula>
                        Formula or equation or chemical formula or something else(if there is one)
                    </formula>
                </summary_piece>
            </summary>
            here is the text that i want you to summarize: {text}"""
    
    # Prepare the API request
    endpoint = f"{server_url}/generate"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    # Include API token if provided

    
    # Prepare payload
    payload = {
        "prompt": prompt,
    }
    
    try:
        # Send the request to the server
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def generate_test(summary, num_questions=5):
    """
    Sends a request to the server to generate a test based on the provided summary.
    
    Args:
        summary (str): The summary XML to create a test from
        num_questions (int): Number of questions to generate
        api_token (str, optional): DeepSeek API token
        server_url (str): The URL of the server
        
    Returns:
        str: The generated test XML
    """

    server_url = 'http://localhost:8000'
    # Format the prompt according to the specified template
    prompt = f"""I have a summary in xml format. Make me a test which consists of {num_questions} questions.
                Each question should have 4 variants of answers.
                Each question should have only one correct answer.
                Each answer must be short and consist of only 1-6 words.
                The correct answer must not always be the first. So it must stand in a randomly counted location.
                The test should be in xml format.
                The test should be in the following format:
                <test>
                    <question>
                        <text>Question text</text>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                        <answer>
                            <text>Answer text</text>
                            <is_correct>true/false</is_correct>
                        </answer>
                    </question>
                </test>
                here is the summary: {summary}"""
    
    # Prepare the API request
    endpoint = f"{server_url}/generate"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    # Prepare payload
    payload = {
        "prompt": prompt,
    }
    
    try:
        # Send the request to the server
        response = requests.post(endpoint, json=payload, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def extract_summary(response):
    # Find the <summary> tag
    start_idx = response.find("<summary>")
    end_idx = response.find("</summary>", start_idx) + len("</summary>")
    
    if start_idx != -1 and end_idx != -1:
        return response[start_idx:end_idx]
    
    # Return the full response if we can't extract the summary
    return response

def extract_test(response):
    """
    Extracts the test XML from the response
    
    Args:
        response (str): The response from the API
        
    Returns:
        str: The extracted test
    """
    # Find the <test> tag
    start_idx = response.find("<test>")
    end_idx = response.find("</test>", start_idx) + len("</test>")
    
    if start_idx != -1 and end_idx != -1:
        return response[start_idx:end_idx]
    
    # Return the full response if we can't extract the test
    return response

def main():
    
    
    server = 'http://localhost:8000'

    what_to_generate = input("What do you need? (summary/test): ")

    # Get text from file or user input
    text = open("test_client_logic/text.txt", "r").read()
    summary = open("test_client_logic/summary.txt", "r").read()
    # Process based on user choice
    if what_to_generate.lower() == "summary":
        print("\nGenerating summary, please wait...")
        summary_response = generate_summary(text)
        
        if summary_response:
            summary = extract_summary(summary_response)
            print("\n--- Generated Summary ---\n")
            print(summary)
            
            # Save to file
            output_file = "summary_output.xml"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"\nSummary saved to {output_file}")
            except Exception as e:
                print(f"Error saving summary: {str(e)}")
                
            # Ask if user wants to generate a test from this summary
            generate_test_prompt = input("\nDo you want to generate a test from this summary? (yes/no): ")
            if generate_test_prompt.lower() in ["yes", "y"]:
                what_to_generate = "test"
                # Continue to test generation
    
    if what_to_generate.lower() == "test":
        # If we don't have a summary yet, we need to generate one first
        print(f"\nGenerating test with {5} questions, please wait...")
        test_response = generate_test(summary)
        
        if test_response:
            test = extract_test(test_response)
            print("\n--- Generated Test ---\n")
            print(test)
            
            # Save to file
            output_file = "test_output.xml"
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(test)
                print(f"\nTest saved to {output_file}")
            except Exception as e:
                print(f"Error saving test: {str(e)}")
    elif what_to_generate.lower() not in ["summary", "test"]:
        print("Invalid option. Please choose 'summary' or 'test'.")

if __name__ == "__main__":
    main() 