# Food bot

### Made with love using [RASA](https://rasa.com/)

This repo contains a chatbot for Food ordering and using Zomato Api for searching best restaurant.
It will reply back with something like "We do not operate in that area yet" if your city is not amoung Tier-1 and Tier-2.

The bot is able to identify common synonyms of city names, such as Bangalore/Bengaluru, Mumbai/Bombay, Allahabad/Prayagraj etc.
The cuisine preference is taken from the customer.

### Steps to run:
1. Create a new python3 virtual environment and do `pip install -r requirements.txt`
2. Clone this [repo](https://github.com/halloTheCoder/foodbot)
3. Run `rasa train` to train NLU and Policies
4. Actions Require a Zomato API creditials. Grab it from [here](https://developers.zomato.com/api)<br>Once you get key, add it in `credentials.sh` under `ZOMATO_API_KEY`.<br>*Basic:* Get free and instant access to restaurant information and search APIs (up to 1000 calls/day) Free tier.
5. Run `chmod +x credentials.sh` and `source ./credentials.sh` 
6. Run `rasa run actions --actions actions.actions` to start the action server.
7. To interact with the assistant in command line, run `rasa interactive`

## Thanks for reading.