import base64
import openai

openai.api_key = ""

# 1. Process Images
# 2. Put Image to chatgpt, get results
# 3. format & display results
def main():
    image_path = "IMG_1366.jpg"
    base64_image = encode_image(image_path)

    response = openai.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "This is a table of contents, "
                                             "you are a computer analysing this table of contents, for each chapter &"
                                             "corresponding subchapter you are directed to give the chapter name and what page it starts on."
                                             "This should be formatted as a list of comma seperated key:value pairings. "
                                             "Only consider the chapters and subchapters with numbers corresponding to them. "
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
        max_tokens=300,
    )

    print(response.choices[0].message.content)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


if __name__ == "__main__":
    main()
