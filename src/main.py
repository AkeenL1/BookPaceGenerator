import base64
import openai
import re
import os

openai.api_key = ""

# 1. Process Images
# 2. Put Image to chatgpt, get results
# 3. format & display results
def main():
    out = {}

    image_path = "../images/IMG_1366.jpg"
    directory_path = '../images'

    # for each image in images folder
    # loop through and encode then send to openai
    # append results to dictionary

    count = 0
    for entry in os.listdir(directory_path):
        full_path = os.path.join(directory_path, entry)
        base64_image = encode_image(full_path)
        print(full_path)

        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "This is a table of contents, "
                                                 "you are a computer analysing this table of contents, for each chapter &"
                                                 "corresponding subchapter you are directed to give what page each chapter is on and the chapter name."
                                                 "This should be formatted as a list of comma seperated key:value "
                                                 "pairings with the key as the page number and the value as the "
                                                 "chapter name, only provide this list. there should be no space in between the key:value. for example"
                                                 "A chapter named 'The Start' on page 5 would look like '5:'The Start'. Each chapter should be a single string not broken up in any way besides spaces"
                                                 "Only consider the chapters and subchapters with numbers corresponding to them. Each chapter Name should start and end with a ' with no spaces between them, for example 'Chapter Name' not ' Chapter Name' "
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )


        pairs = response.choices[0].message.content.split(',')
        for pair in pairs:
            split_pair = pair.split(':')
            if len(split_pair) == 2:
                key, value = split_pair
                cleaned_key = re.sub(r'[^\d]', '', key.strip())
                cleaned_val = value.replace("'", "")
                if cleaned_key:
                    int_key = int(cleaned_key.strip())
                    out[int_key] = cleaned_val.strip()


    sorted_dict = {k: out[k] for k in sorted(out)}
    print(sorted_dict)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == "__main__":
    main()
