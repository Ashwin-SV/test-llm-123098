from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.schema import SystemMessage
from langchain_mistralai.chat_models import ChatMistralAI

from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig

import chainlit as cl

import os 
# Manually setting the secret key
os.environ["CHAINLIT_AUTH_SECRET"] = "W7x0Hbt?c6lEAW3^ZV_>Xaa0XG6QxkAj56NNFbXrK^:W-?rqHDIpQ87,aGR4UJ3A"
# Now, you can use os.environ to access "YOUR_SECRET_KEY_NAME" throughout your application 
secret_key = os.environ.get("CHAINLIT_AUTH_SECRET")

@cl.password_auth_callback
def auth_callback(username: str, password: str):     # Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == ("admin", "admin"):
        return cl.User(
            identifier="admin", metadata={"role": "admin", "provider": "credentials"}
        )
    else:
        return None


@cl.on_chat_start
async def on_chat_start():
    chat_model = ChatMistralAI(
    endpoint="https://Mistral-large-12thmanai-serverless.eastus2.inference.ai.azure.com",
    mistral_api_key="HOWUkjG3D77sfGvL2bkerPISTxbuXMaU", temperature = 0.5, max_tokens = 400
)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're a very knowledgeable historian who provides accurate and eloquent answers to historical questions.",
            ),
            ("human", "{question}"),
        ]
    )
    runnable = prompt | chat_model | StrOutputParser()
    cl.user_session.set("runnable", runnable)
    await cl.Message(
        author="12th Man AI", content="Hello! Im an AI assistant, trained on site safety inspection reports. How may I help you?"
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable

    msg = cl.Message(content="", author="12th Man AI")

    async for chunk in runnable.astream(
        {"question": message.content},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()]),
    ):
        await msg.stream_token(chunk)

    await msg.send()