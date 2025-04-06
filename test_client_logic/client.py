import requests

def generate_summary(text):

    server_url="http://localhost:8000"
    # Prepare the API request
    endpoint = f"{server_url}/generate_summary"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }

    payload = {
        "text": text,
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


    server_url = 'http://localhost:8000'
    
    # Prepare the API request
    endpoint = f"{server_url}/generate_test"
    
    headers = {
        "Content-Type": "application/json",
        "accept": "application/json"
    }
    
    # Prepare payload
    payload = {
        "text": summary,
        "num_questions": num_questions
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

    what_to_generate = input("What do you need? (summary/test): ")

    # Get text from file or user input
    text = open("text.txt", "r").read()
    summary = open("summary.txt", "r").read()


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