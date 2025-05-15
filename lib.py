from ollama import chat
from ollama import ChatResponse

from dateutil import parser
import pandas as pd
import numpy as np

__hallucination_sampling_size = 20

def check_self_knowledge(anime_name: str):
    prompt_template = f"""You are Anime Master.

    For anime name, "{anime_name}".

    Answer in exactly this format:
    {{releaseDate(YYYY/MM)}}|{{oneGenre}}|{{numberOfEpisodes}}
    Only output this line, no extra text or explanation.

    If you don't know the answer, please output exactly text "###UNKNOWN"
    """

    with open("temp/raw_input.csv", "w", encoding="utf-8") as f:
        for i in range(__hallucination_sampling_size):
            response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': prompt_template,
            },
            ])
            
            f.write(f"{response.message.content}\n")

            if response.message.content.find('UNKNOWN') >= 0:
                # quick response unknown
                return False

    # clean up data
    df = pd.read_csv("temp/raw_input.csv", delimiter='|', header=None, on_bad_lines='skip')
    with open("temp/intermediate.csv", "w", encoding="utf-8") as f:
        for line in [str(x).strip() for x in df[0].to_list()]:
            tokens = line.split('/')
            if len(tokens) == 0:
                continue
            f.write(f"{tokens[0]},{parser.parse(line).strftime('%Y/%m')}\n")
    
    # Use Log-Likelihood to measure the level of hallucinations
    weight_year_column = 1
    weight_year_month_column = 0.15

    df = pd.read_csv("temp/intermediate.csv", header=None)
    n_rows = len(df)

    # Calculate frequency (count) for each unique 'year' and 'year-and-month'
    year_counts = df[0].value_counts()
    year_month_counts = df[1].value_counts()

    # Map frequencies back to the dataframe
    df['year_likelihood'] = df[0].map(lambda x: (year_counts[x] / n_rows) ** weight_year_column)
    df['year_month_likelihood'] = df[1].map(lambda x: (year_month_counts[x] / n_rows) ** weight_year_month_column)

    # Sum of likelihoods, which is negative number, more negative less likelihood
    df['log_likelihood'] = np.log(df['year_likelihood']) + np.log(df['year_month_likelihood'])

    average_likelihood = (np.average(df['log_likelihood']))

    print(f"level of my uncertain = {average_likelihood}")

    return bool(np.abs(average_likelihood) < 1)