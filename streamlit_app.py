import streamlit as st
from openai import OpenAI
from typing import Optional
import requests
import logging
import httpx
import json

BASE_API_URL = "http://h3875247.eero.online:7860"
LANGFLOW_ID = "8994f052-0cf8-4676-9e38-8da0b7ec52aa"
FLOW_ID = "83a184b6-ee79-449e-a475-3fc274877330"
APPLICATION_TOKEN = "AstraCS:tFXyGCzeKxfELaHIzuIUydKS:7e87cf958201164e9e6c3f14b35f488f968798e42fb53189cf8eaec4ef5f0625"
ENDPOINT = ""

TWEAKS = {
  "Agent-SdiBn": {},
  "ChatInput-4kutE": {},
  "ChatOutput-NOh69": {},
  "URL-PIs2Y": {},
  "AstraDBToolComponent-ySG1w": {},
  "CurrentDate-XmCTz": {},
  "Agent-O0gYO": {},
  "CalculatorTool-u61I5": {},
  "CustomComponent-0FwpH": {},
  "CustomComponent-D5n6F": {},
  "Agent-kog4j": {}
}

# Show title and description.
st.title("💬 Chatbot")
st.write(
    "This is a simple chatbot that uses OpenAI's GPT-3.5 model to generate responses. "
    "To use this app, you need to provide an OpenAI API key, which you can get [here](https://platform.openai.com/account/api-keys). "
    "You can also learn how to build this app step by step by [following our tutorial](https://docs.streamlit.io/develop/tutorials/llms/build-conversational-apps)."
)

def run_flow(message: str,
  endpoint: str,
  output_type: str = "chat",
  input_type: str = "chat",
  tweaks: Optional[dict] = None,
  api_key: Optional[str] = None) -> dict:
    """
    Run a flow with a given message and optional tweaks.

    :param message: The message to send to the flow
    :param endpoint: The ID or the endpoint name of the flow
    :param tweaks: Optional tweaks to customize the flow
    :return: The JSON response from the flow
    """
    api_url = f"{BASE_API_URL}/api/v1/run/{endpoint}"

    payload = {
        "input_value": message,
        "output_type": output_type,
        "input_type": input_type,
    }
    headers = None
    if tweaks:
        payload["tweaks"] = tweaks
    if api_key:
        headers = {"x-api-key": api_key}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

def is_healthy():
    try:
        url = f"{BASE_API_URL}/health"
        response = httpx.get(url)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return False

def initiate_session(flow_id, input_value, stream: bool = False):
    url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{flow_id}?stream={stream}"
    headers = {"Authorization": "Bearer " + APPLICATION_TOKEN, "Content-Type": "application/json"}
    data = {
        "input_value": input_value
    }

    response = httpx.post(url, json=data, headers=headers)
    response.raise_for_status()
    if(response.status_code ==200):
        return response.json()
    else:
        raise Exception("Failed to initiate session")

def stream_response(stream_url, session_id):
    stream_url = f"{BASE_API_URL}{stream_url}"
    params = {"session_id": session_id}

    with httpx.stream("GET", stream_url, params=params, timeout=None) as response:
        for line in response.iter_lines():
            logging.info(f"Line: {line}")

# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
#if not openai_api_key:
#    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
#else:

# Create an OpenAI client.
#client = OpenAI(api_key=openai_api_key)

# Create a session state variable to store the chat messages. This ensures that the
# messages persist across reruns.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message. This will display
# automatically at the bottom of the page.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    message = st.session_state.messages[len(st.session_state.messages) - 1]["content"]

    # Generate a response using the OpenAI API.
    #stream = client.chat.completions.create(
    #    model="gpt-3.5-turbo",
    #    messages=[
    #        {"role": m["role"], "content": m["content"]}
    #        for m in st.session_state.messages
    #    ],
    #    stream=True,
    #)

    print(f"Input message:{message}")

    response = run_flow(
        message=json.dumps(message),
        endpoint=FLOW_ID,
    )

    print(response)
    print("*******")

    try:
       # init_response = initiate_session(
       #     flow_id=FLOW_ID,
       #     input_value=st.session_state.messages[len(st.session_state.messages) - 1]['content'],
       #     stream=True
       # )

        #session_id = init_response["session_id"]
        #has_stream_url = "stream_url" in init_response["outputs"][0]["outputs"][0]["artifacts"]

        #stream_url = init_response["outputs"][0]["outputs"][0]["artifactss"]["stream_url"]
 

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            AIResponse = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]
            st.write(AIResponse)
        st.session_state.messages.append({"role": "assistant", "content": AIResponse})

    except Exception as e:
        logging.exception(f"Error: {str(e)}")
                                    
    
