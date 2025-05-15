from ollama import chat
from ollama import ChatResponse

from extract import retrieve_anime_information
from lib import check_self_knowledge

if __name__ == "__main__":
    # anime_name = "Love live school idol"
    print ("Hey there! I'm Anime Guru, and I'm here to give you a quick and fun summary of your favorite anime. Just type the name of the anime, and I'll take care of the rest!\n")

    anime_name = input("Name: ")

    print(f'Checking my knowledge on {anime_name}...')

    if check_self_knowledge(anime_name):
        print("It seems I know this Anime, let me give some brief...")

        prompt_template = f"""You are Anime Master.

        For anime name, "{anime_name}".

        Please give some short summarize to advertise newcomer.
        """

        response: ChatResponse = chat(model='llama3.2', messages=[
        {
            'role': 'user',
            'content': prompt_template,
        },
        ])
        print(response.message.content)

    else:
        print("I didn't watch this, but let me review this for you...")
        anime_info = retrieve_anime_information(anime_name)

        prompt_template = f"""You are Anime Master.

        Please summary below information of Anime "{anime_name}" to adverise newcomer:

        {anime_info}
        """   

        response: ChatResponse = chat(model='llama3.2', messages=[
            {
                'role': 'user',
                'content': prompt_template,
            },
            ])
        print(response.message.content)
        # print(f"Sorry, I don't know Anime name {anime_name}")
