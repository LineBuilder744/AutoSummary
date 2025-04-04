def get_raw_test_xml(text):
    """
    Takes a string and cuts out everything before the <test> tag.
    
    Args:
        text (str): The input text with XML content
        
    Returns:
        str: The text starting from the <test> tag, or the original text if tag not found
    """
    tag = "<test>"
    tag_pos = text.find(tag)
    
    if tag_pos != -1:
        return text[tag_pos:]
    return text

def get_raw_summary_xml(text):
    """
    Takes a string and cuts out everything before the <summary> tag.
    
    Args:
        text (str): The input text with XML content
        
    Returns:
        str: The text starting from the <summary> tag, or the original text if tag not found
    """
    tag = "<summary>"
    tag_pos = text.find(tag)
    
    if tag_pos != -1:
        return text[tag_pos:]
    return text 