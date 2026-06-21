MIN_TEXT_LENGTH = 500
MAX_TEXT_LENGTH = 50000

# function to validate the input text for quiz generation, checking for presence, length constraints, and returning a message indicating whether the text is valid 
def validate_text(text):
    if not text or not text.strip():
        return False, "No text was provided."

    text = text.strip()

    if len(text) < MIN_TEXT_LENGTH:
        return False, f"Text is too short. Minimum is {MIN_TEXT_LENGTH} characters."

    if len(text) > MAX_TEXT_LENGTH:
        return False, f"Text is too long. Maximum is {MAX_TEXT_LENGTH} characters."

    return True, "Text is valid."