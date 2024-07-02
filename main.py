import json
import requests

# Carregar o arquivo de configuração
with open('config.json', 'r') as config_file:
    config = json.load(config_file)

accesstoken = config['accesstoken']
pipeid = config['pipeid']
triagemphaseid = config['triagemphaseid']
fechadophaseid = config['fechadophaseid']

headers = {'Authorization': f'Bearer {accesstoken}', 'Content-Type': 'application/json'}

query = """
{
  allCards(pipeId: %s) {
    edges {
      node {
        id
        current_phase {
          id
        }
      }
    }
  }
}
""" % pipeid

response = requests.post('https://api.pipefy.com/graphql', json={'query': query}, headers=headers)

# Verifique o status da resposta da primeira requisição
if response.status_code == 200:
    response_json = response.json()
    # Verifique se 'data' está presente na resposta JSON
    if 'data' in response_json and 'allCards' in response_json['data']:
        cards = response_json['data']['allCards']['edges']

        # Filtrar os cartões que estão na fase "Triagem"
        cards_in_triagem = [card for card in cards if card['node']['current_phase']['id'] == triagemphaseid]

        # Mover cada card para a fase "Fechado"
        for card in cards_in_triagem:
            card_id = card['node']['id']
            mutation = """
            mutation {
                moveCardToPhase(input: { card_id: %s, destination_phase_id: %s }) {
                    card {
                        id
                    }
                }
            }
            """ % (card_id, fechadophaseid)

            # Faça a requisição para mover o card
            move_response = requests.post('https://api.pipefy.com/graphql', json={'query': mutation}, headers=headers)

            # Verifique o status da resposta
            if move_response.status_code == 200:
                print(f'Card {card_id} movido com sucesso.')
            else:
                print(f'Falha ao mover o card {card_id}. Status: {move_response.status_code}, Resposta: {move_response.text}')
    else:
        print(f'Resposta inesperada: {response_json}')
else:
    print(f'Falha na requisição. Status: {response.status_code}, Resposta: {response.text}')