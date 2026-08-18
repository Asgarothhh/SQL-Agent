from services.graph import agent

question = "имена всех покупателей?"

stream = agent.stream_events(
    {"messages":[{"role":"user", "content": question}]},
    version="v3"
)

for message in stream.messages:
    for token in message.text:
        print(token, end = "")

final_state = stream.output