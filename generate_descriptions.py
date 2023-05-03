import openai
from openai.error import RateLimitError
import time

# write a function that calls openai chan complete api and returns the generated text
def generate_image_descriptions(text, model):
    """
    Generate image descriptions for a given text using the OpenAI API.

    Args:
        text (str): Text to be described.
        model (str): Name of the model to be used.
        api_key (str): OpenAI API key.

    Returns:
        str: Description of the text.

    Raises:
        None
    """
    prompt = f"""Generate an image description useful for stable-diffusion generator model based on this piece of text:
    '{text}'
    """
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}]
            )
    return response.choices[0].message.content


def generate_image_descriptions_safely(text, model):
    """
    Generate image descriptions for a given text using the OpenAI API. 
    This function waits 5 seconds if the API returns an error.

    Args:
        text (str): Text to be described.
        model (str): Name of the model to be used.
        api_key (str): OpenAI API key.

    Returns:
        str: Description of the text.

    Raises:
        None
    """
    try:
        return generate_image_descriptions(text, model)
    except RateLimitError:
        print('Rate limit exceeded. Waiting 5 seconds...')
        time.sleep(5)
        return generate_image_descriptions_safely(text, model)