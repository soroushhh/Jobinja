import string
import json
import re
from pathlib import Path


# load json file
with Path(
    "C:/Users/SoroushPC/OneDrive/Documents/Projects/Jobinja/app/jobinja_demo.json"
).open(mode="r") as f:
    data = json.load(f)


def normalize_title_string(txt):
    """ remove unnecassary chars from string and then extract key words in recruiments title """
    mapper = {")": "", "(": ""}
    # convert given string to chars to make it easier for extracting key words
    txt_list = txt.split()

    # to remove redundant chars from elemts in the list
    for i in range(len(txt_list)):
        for key, value in mapper.items():
            txt_list[i] = txt_list[i].replace(key, value)

    # title keywords contain english characters, so we want to extract the words that contain ASCII chars, if there is no ASCII in title we return the whole title
    pattern = re.compile(r"\w", re.ASCII)

    # to create a new list that contain key words from title
    result = list(filter(lambda x: pattern.match(x), txt_list))
    if result:
        return (" ").join(result)
    return (" ").join(txt_list)


def normalize_location_string(txt):
    """To omit the unwanted characters
    Input Parameter Example ---> 'تهران\n                                                ، تهران'
    Expected output Example ---> ("تهران", "تهران")
    """
    txt = txt.replace("،", "")
    txt = txt.split("\n")

    prov, city = txt[0], txt[1].strip()
    output = (prov, city)
    return output


def normalize_salary_string(txt):
    """extract salary amount from given string if it exists and convert it to an integer number
    Input Parameter Example ---> حقوق از ۱۰,۰۰۰,۰۰۰ تومان
    Expected output Example ---> 10000000
    """
    # define senarios with non-numeric characters
    combos = [
        ("حقوق توافقی", "Negotiable"),
        ("حقوق حقوق پایه (وزارت کار)", "Based salary"),
    ]

    # normalize non numeric characters
    for combo in combos:
        if txt == combo[0]:
            txt = combo[1]
            return txt

    # senarios that contain numeric characters
    from_char = "۱۲۳۴۵۶۷۸۹۰"
    to_char = "1234567890"

    for i in range(len(to_char)):
        txt = txt.replace(from_char[i], to_char[i])

    # remove non numeric characters from txt
    pattern = re.compile(r"[^\d]")
    txt = pattern.sub("", txt)
    return int(txt)


def normalize_gender_string(txt):
    """Convert non-ascii characters into English
    Different senarios ---> (زن , مرد , مهم نیست)
    Expected output ---> (Women, Man, Any)"""

    from_char = ("زن", "مرد", "مهم نیست")
    to_char = ("Woman", "Man", "Any")

    for old, replm in zip(from_char, to_char):
        if txt == old:
            txt = replm

    return txt


def normalize_colab_type_string(value):
    """To translate non-ascii characters into English
    Different input senarios ---> ("دور کاری", "تمام وقت", "پاره وقت", "کارآموزی")
    Expected output ---> ("Remote", "Full-time", "Part-time", "Intership")"""

    from_char = ("دور کاری", "تمام وقت", "پاره وقت", "کارآموزی")
    to_char = ("Remote", "Full-time", "Part-time", "Intership")

    # handle both string and list inputs
    if type(value) == list:
        # copy list object cause we're about to mutate it
        value = value[:]

        for i in range(len(value)):
            for old, replacement in zip(from_char, to_char):
                if value[i] == old:
                    value[i] = replacement

        return value

    # handle string input
    for old, replacement in zip(from_char, to_char):
        if value == old:
            value = replacement
    return value


def normalize_experience_string(txt):
    """To transform non-ascii characters into english
    Input type ---> ("مهم نیست", "کمتر از سه سال", "سه تا هفت سال", "بیش از هفت سال")
    expected output ---> ("Any", "Less than 3 years", "3 to 7 years", "More than 7 years")
    """
    from_char = ("مهم نیست", "کمتر از سه سال", "سه تا هفت سال", "بیش از هفت سال")
    to_char = ("Any", "Less than 3 years", "3 to 7 years", "More than 7 years")

    for old, replacement in zip(from_char, to_char):
        if txt == old:
            txt = replacement

    return txt


def main():
    for ad in data["data"]:
        for key, value in ad.items():
            if key == "title":
                ad[key] = normalize_title_string(value)
            elif key == "Type":
                ad[key] = "Web, Programming and Software"
            elif key == "Provience/City":
                ad[key] = normalize_location_string(value)
            elif key == "Salary":
                ad[key] = normalize_salary_string(value)
            elif key == "Gender":
                ad[key] = normalize_gender_string(value)
            elif key == "Colab Type":
                ad[key] = normalize_colab_type_string(value)
            elif key == "Min of year Exp":
                ad[key] = normalize_experience_string(value)
            # elif key == "Military Service":
            #     print(value)

    # save the changes in a new json file in the current working dir
    with Path(
        "C:/Users/SoroushPC/OneDrive/Documents/Projects/Jobinja/app/mod_jobinja.json"
    ).open("w", encoding="utf-8") as output_file:
        json.dump(data, output_file, indent=3, ensure_ascii=False)


if __name__ == "__main__":
    main()